function doGet() {
  return ContentService.createTextOutput("Google App Script Acknowledges Get");
}
function doPost(d) {
  const TIME_ZONE = "GMT+7";
  const TITLE = ["When","LIGHT","CO2"]

  try {
    var data  = JSON.parse(d.postData.contents);
    if (data == undefined) {
      return ContentService.createTextOutput("Wrong parameters!\r\n");
    } else {
      var ss = SpreadsheetApp.openById(data.Sheet_id);
      var sheet = ss.getSheets()[0]                     // Use first Sheet in WorkSheet
      var row = sheet.getLastRow() + 1;
      if (row == 1) {                     // append TITLE at first row if Sheet empty
        sheet.appendRow(TITLE)
        row += 1
      }

      sheet.getRange(row, 1).setValue(Utilities.formatDate(new Date(), TIME_ZONE, "dd.MM.yyyy HH:mm:ss"));
      sheet.getRange(row, 2).setValue(data.Light || "no data");
      sheet.getRange(row, 3).setValue(data.CO2|| "no data");
      SpreadsheetApp.flush();

      return ContentService.createTextOutput("Google App Posted to Google Sheet\r\n");
    }
  } catch(e) {
    return ContentService.createTextOutput("GoogleSheetApp ERROR!\r\n" + e.message);
  }
}
