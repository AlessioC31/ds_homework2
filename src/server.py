from definitions import def_pb2
from definitions import def_pb2_grpc

import random
import grpc
from concurrent.futures import ThreadPoolExecutor

class TemperatureSensor(def_pb2_grpc.TemperatureSensorServicer):
    def SensorInfo(self, request, context):
        sensor_uid = request.uid

        # Use sensor_uid to query Sensor Info
        # ...

        response = def_pb2.SensorInfoResponse()
        response.name = "sensor"
        response.state = def_pb2.SensorInfoResponse.UP if random.random() < 0.5 else def_pb2.SensorInfoResponse.DOWN
        response.latitude = random.random()
        response.longitude = random.random()
        response.altitude = random.random()

        return response

    def SensorData(self, request, context):
        # use request.uid to query temperature measurements
        # return 10 dummy temperature measurements

        for _ in range(10):
            yield def_pb2.TemperatureData(temperature = random.uniform(30, 40))

class ObjectDetection(def_pb2_grpc.ObjectDetectionServicer):
    def SummaryDetection(self, request_iterator, context):
        num_people = 0
        num_cars = 0
        num_trucks = 0
        for image in request_iterator:
            # analyze image.image_data
            num_people += random.randint(0, 5)
            num_cars += random.randint(0, 4)
            num_cars += random.randint(0, 1)

        return def_pb2.SummaryResponse(num_people=num_people, num_cars=num_cars, num_trucks=num_trucks)

    def Detect(self, request_iterator, context):
        def generateRandomDetection(image):
            frame_id = image.frame_id

            bb_height = random.randrange(0, image.height)
            bb_width = random.randrange(0, image.width)
            bb_x = random.randrange(0, image.width - bb_width)
            bb_y = random.randrange(0, image.height - bb_height)

            bb = def_pb2.BoundingBox(x=bb_x, y=bb_y, width=bb_width, height=bb_height)

            cat = random.randint(0, 2)

            return def_pb2.Detection(
                bounding_box=bb,
                frame_id=frame_id,
                category=cat,
            )

        for image in request_iterator:
            ndetections = random.randint(1,3)

            detections = def_pb2.Detections()
            detections.list.extend(
                map(
                    lambda _: generateRandomDetection(image),
                    range(ndetections)
                )
            )

            yield detections

def serve():
    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    def_pb2_grpc.add_TemperatureSensorServicer_to_server(TemperatureSensor(), server)
    def_pb2_grpc.add_ObjectDetectionServicer_to_server(ObjectDetection(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()