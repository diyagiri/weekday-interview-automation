/**
 * Airtable Scripting App Script
 * Task 1: Split interview rounds into separate rows
 *
 * This script is intended to be run inside Airtable's Scripting extension
 * and is not meant for local execution.
 */
// CONFIG
const rawTable = base.getTable("Raw_Import");
const outTable = base.getTable("Interview_Rounds");

// Field names as they appear in CSV
const F = {
  company: "Company",
  interviewer: "Interviewer",
  interviewerEmail: "Interviewer Email",
  candidate: "Candidate",
  candidateEmail: "Candidate Email",
  scheduling: "Scheduling Method",
  addedOn: "Added On",
};

// LOAD
const rawQuery = await rawTable.selectRecordsAsync();
let batch = [];

for (const r of rawQuery.records) {
  const schedulingRaw = r.getCellValueAsString(F.scheduling).trim();
  if (!schedulingRaw) continue;

  // Split by newlines 
  const lines = schedulingRaw
    .split(/\r?\n/)
    .map(x => x.trim())
    .filter(Boolean);

  for (const line of lines) {
    // Parse "Round1: https://...."
    const match = line.match(/^([^:]+):\s*(https?:\/\/\S+)$/i);
    if (!match) continue;

    let round = match[1].trim();
    round = round.replace(/round\s*0*(\d+)/i, "Round $1");

    const calendly = match[2].trim();

    batch.push({
      fields: {
        "Company": r.getCellValueAsString(F.company).trim(),
        "Interviewer": r.getCellValueAsString(F.interviewer).trim(),
        "Interviewer Email": r.getCellValueAsString(F.interviewerEmail).trim(),
        "Candidate": r.getCellValueAsString(F.candidate).trim(),
        "Candidate Email": r.getCellValueAsString(F.candidateEmail).trim(),
        "Added On": r.getCellValue(F.addedOn),

        "Rounds": round,
        "Calendly Link": calendly,

        // For later tasks
        "Mail Status": { name: "Pending" },
      }
    });

    // Airtable limit
    if (batch.length === 50) {
      await outTable.createRecordsAsync(batch);
      batch = [];
    }
  }
}

// Flush remaining
if (batch.length) {
  await outTable.createRecordsAsync(batch);
}

output.text("✅ Task 1 complete: created one row per round in Interview_Rounds.");
