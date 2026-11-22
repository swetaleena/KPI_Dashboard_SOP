/**
 * Google Apps Script for the Google Sheets path.
 * Sheet tabs required: kpi_status, sop_steps, tasks (see BUILD_GUIDE.md, Path A, Step 6).
 *
 * What it does: for every KPI in 'alert' or 'critical' that has a linked SOP, it adds the SOP checklist
 * to the 'tasks' tab (once, unless a task for that SOP is still open) and notifies Slack or email.
 */
const SLACK_WEBHOOK = '';          // paste a Slack incoming-webhook URL, or leave empty to use email
const NOTIFY_EMAIL = '';           // leave empty to email the sheet owner

function checkKpisAndCreateTasks() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const status = ss.getSheetByName('kpi_status').getDataRange().getValues();
  const steps = ss.getSheetByName('sop_steps').getDataRange().getValues();
  const tasks = ss.getSheetByName('tasks');
  const existing = tasks.getDataRange().getValues();
  const createdFor = [];
  const lines = [];

  // kpi_status columns: A kpi, B value, C direction, D alert_at, E critical_at, F sop_id, G owner_role, H status
  for (let i = 1; i < status.length; i++) {
    const kpi = status[i][0], value = status[i][1], sopId = status[i][5], owner = status[i][6], state = status[i][7];
    if (!sopId || (state !== 'alert' && state !== 'critical')) continue;
    if (createdFor.indexOf(sopId) !== -1) continue;

    // tasks columns: A task_id, B created_at, C kpi, D sop_id, E owner_role, F severity, G step_no, H step, I evidence, J done
    const open = existing.slice(1).some(r => r[3] === sopId && r[9] !== true);
    if (open) continue;

    const taskId = 'T' + Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyMMddHHmm') + '-' + sopId;
    const rows = steps.slice(1).filter(s => s[0] === sopId)
      .map(s => [taskId, new Date(), kpi, sopId, owner, state, s[1], s[2], s[4], false]);
    if (rows.length === 0) continue;
    tasks.getRange(tasks.getLastRow() + 1, 1, rows.length, rows[0].length).setValues(rows);
    createdFor.push(sopId);
    lines.push((state === 'critical' ? '🔴 ' : '🟠 ') + kpi + ' = ' + Number(value).toFixed(3) +
               ' → run SOP "' + sopId + '" (owner: ' + owner + ')');
  }

  if (lines.length === 0) return;
  const text = 'KPI alerts:\n' + lines.join('\n');
  if (SLACK_WEBHOOK) {
    UrlFetchApp.fetch(SLACK_WEBHOOK, { method: 'post', contentType: 'application/json', payload: JSON.stringify({ text: text }) });
  } else {
    MailApp.sendEmail(NOTIFY_EMAIL || Session.getActiveUser().getEmail(), 'KPI alerts: action needed', text);
  }
}
