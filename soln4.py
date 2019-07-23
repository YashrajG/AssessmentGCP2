# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud import datastore
import logging

def hello_gcs(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    #print(event)
    
    if event['contentType'] not in ['image/png', 'image/jpeg', 'image/gif', 'image/bmp', 'image/webp', 'image/vnd.microsoft.icon', 'application/pdf', 'image/tiff']:
        logging.debug("Non image type " + event['contentType'] + " file detected")
        return
    else: 
        logging.info(event['contentType'] + " file detected")

    # Instantiates a client
    client = vision.ImageAnnotatorClient()
    image = vision.types.Image()
    image.source.image_uri = 'gs://{}/{}'.format(event['bucket'], event['name'])

    objects = client.object_localization(image=image).localized_object_annotations
    ds_client = datastore.Client()
    list1 = []
    print('Number of objects found: {}'.format(len(objects)))
    for object_ in objects:
        entity = datastore.Entity(ds_client.key('Object_Detection', event['name'] + "/" + object_.name))
        list1.append(event['name'])
        list1.append(object_.name)
        list1.append(object_.score)
        print('\n{} (confidence: {})'.format(object_.name, object_.score))
        print('Normalized bounding polygon vertices: ')
        for vertex in object_.bounding_poly.normalized_vertices:
            print(' - ({}, {})'.format(vertex.x, vertex.y))
            list1.append(str((vertex.x,vertex.y)))
        entity.update({
            'FileName' : list1[0] ,
            'ObjectName' : list1[1] ,
            'confidence' : list1[2] ,
            'vertex1' : list1[3] ,
            'vertex2' : list1[4] ,
            'vertex3' : list1[5] ,
            'vertex4': list1[6]
            })
        list1 = []
