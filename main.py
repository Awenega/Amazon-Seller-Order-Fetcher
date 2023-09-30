from report import getReportId, getReportDocumentId, getReportDocumentURL, getDocument
from datetime import datetime, timezone, timedelta

def main():

    startDate = (((datetime.now() - timedelta(1)).replace(hour=0, minute=0, second=0, microsecond=0)).astimezone(timezone.utc)).isoformat()
    endDate = ((datetime.now() - timedelta(minutes=3)).astimezone(timezone.utc)).isoformat()
    
    reportId = getReportId(startDate, endDate)
    reportDocumentId = getReportDocumentId(reportId)
    reportDocumentURL = getReportDocumentURL(reportDocumentId)
    reportOrdersJson = getDocument(reportDocumentURL)
    print(reportOrdersJson)

if __name__ == "__main__":
    main()
