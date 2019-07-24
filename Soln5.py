import base64
from google.cloud import monitoring_v3
from datetime import datetime
import time
import csv

def hello_pubsub(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    #pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    #print(pubsub_message)
    client = monitoring_v3.MetricServiceClient()
    project_name = client.project_path("pe-training")
    interval = monitoring_v3.types.TimeInterval()
    now = time.time()
    interval.end_time.seconds = int(now)
    interval.end_time.nanos = int(
        (now - interval.end_time.seconds) * 10**9)
    interval.start_time.seconds = int(now - (7*24*60*60))
    interval.start_time.nanos = interval.end_time.nanos
    aggregation = monitoring_v3.types.Aggregation()
    aggregation.alignment_period.seconds = 24*60*60  # 20 minutes
    aggregation.per_series_aligner = (
        monitoring_v3.enums.Aggregation.Aligner.ALIGN_MEAN)

    csvName = "instancesMetric_" + str(datetime.date.today()) + ".csv"
    csvRow = []
    results = client.list_time_series(project_name,'metric.type = "compute.googleapis.com/instance/cpu/utilization"',interval,monitoring_v3.enums.ListTimeSeriesRequest.TimeSeriesView.FULL,aggregation)
    with open(csvName, "w") as csvFile:
        csvWriter = csv.writer(csvFile)
        for result in results:
            print(result.metric.labels["instance_name"]) # Instance Name
            print(result.resource.labels["instance_id"]) # Instance ID
            csvRow.append(result.metric.labels["instance_name"])
            csvRow.append(result.resource.labels["instance_id"])
            for point in result.points:
                startTime = datetime.utcfromtimestamp(point.interval.start_time.seconds).strftime('%Y-%m-%d %H:%M:%S')
                endTime = datetime.utcfromtimestamp(point.interval.end_time.seconds).strftime('%Y-%m-%d %H:%M:%S')
                print(startTime) # Start Time
                print(endTime) # End Time
                print(point.value.double_value) # CPU Utilisation between above time points
                csvRow.append(startTime)
                csvRow.append(endTime)
                csvRow.append(point.value.double_value)
        csvWriter.writerow(csvRow)
    
    # TODO put in CSV
    # TODO mail to DevOPS