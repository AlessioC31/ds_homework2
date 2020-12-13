# Distributed Systems 2020/2021 Homework 2 - Alessio Cosenza

## Introduction
In the field of client-server communication protocols, one of the most used protocol is **HTTP**, based on the **Request-Reply protocol**. In these years different alternatives where proposed, one of which is the **RPC** (**R**emote **P**rocedure **C**all) procol. The purpose of this homework is to provide a basic client-server implementation using **gRPC**: an RPC implementation provided by **Google**.

Firstly, a brief introduction on RPC and gRPC is provided.

## RPC

**RPC** allows clients to call procedures in server programs running on machines different than the one where the client is running. Similarly to how modern programming languages work, in a RPC environment, servers use the concept of **interfaces**. An interface is defined as a description of the services an object can provide. Using this paradigm, clients don't need to know the underlying implementation of the procedures they invoke, in this way the protocol is language-agnostic: a Python client can invoke procedures exposed by a Node.js server.

Commonly, RPC protocols use an **Interface Definition Language** (**IDL**), in order to define services' interfaces.

## gRPC

gRPC is the Google implementation of the RPC protocol. The IDL used by gRPC is Protocol Buffers, a tool already discussed in Homework 1. Probuf provides a way to define services using `service` and `rpc` keywords, for example:

```
service TemperatureSensor {
    rpc SensorInfo(Sensor) returns (SensorInfoResponse);

    rpc SensorData(Sensor) returns (stream TemperatureData);
}
```

Where `Sensor`, `SensorInfoResponse` and `TemperatureData` are previously defined messages. 

In the example above we defined a service called `TemperatureSensor` which exposes 2 rpcs: `SensorInfo` and `SensorData`. The first one accepts as input a message of type `Sensor` and returns a message of type `SensorInfoResponse`. The second also accepts a `Sensor` as input and returns a stream of `TemperatureData`. 

As we will see in the following implementation, gRPC supports basic request-reply calls, response stream, request stream and bidirectional streams.

## Implementation

The two services defined mimics the interfaces that could possibly be exposed by a temperature sensor and by an object detection server. 

The first one is called `TemperatureSensor` and exposes 2 rpcs: `SensorInfo` and `SensorData`. `SensorInfo` accepts a `Sensor` as input and answers with `SensorInfoResponse`, a message containing basic information about the Sensor requested. `SensorData` accepts a `Sensor` as input and returns, as a stream, a list of `TemperatureData` (measurements done by the sensor).

The second one is called `ObjectDetection` and exposes 2 rpcs: `SummaryDetection` and `Detect`. `SummaryDetection` accepts as input a stream of `Image` and returns a `SummaryResponse`, a message containing information about all the cars, people and trucks detected in the stream provided. `Detect` accepts a stream of `Image` and returns a stream of `Detections`, so for each Image received in the stream, it responds with information about people, cars and trucks detected in the image.

The complete `.proto` definition can be seen here:

```
syntax = "proto3";

package ds_homework2;

message Sensor {
    int32 uid = 1;
}

message SensorInfoResponse {
    enum SensorState {
        UP = 0;
        DOWN =  1;
    }

    string name = 1;
    SensorState state = 2;
    float latitude = 3;
    float longitude = 4;
    float altitude = 5;
}

message TemperatureData {
    float temperature = 1;
}

service TemperatureSensor {
    rpc SensorInfo(Sensor) returns (SensorInfoResponse);

    rpc SensorData(Sensor) returns (stream TemperatureData);
}

message Image {
    int32 width = 1;
    int32 height = 2;
    bytes image_data = 3;
    int32 frame_id = 4;
}

message BoundingBox {
    int32 x = 1;
    int32 y = 2;
    int32 width = 3;
    int32 height = 4;
}

message Detection {
    BoundingBox bounding_box = 1;
    int32 frame_id = 2;

    enum Category {
        Person = 0;
        Car = 1;
        Truck = 2;
    }

    Category category = 3;
}

message Detections {
    repeated Detection list = 1;
}

message SummaryResponse {
    int32 num_people = 1;
    int32 num_cars = 2;
    int32 num_trucks = 3;
}

service ObjectDetection {
    rpc SummaryDetection(stream Image) returns (SummaryResponse);
    rpc Detect(stream Image) returns (stream Detections);
}
```

### Server implementation

The server implementation can be read in `src/server.py`. It also reported here:

```python
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

        # dummy random data is generated
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

            # generate random detections
            num_people += random.randint(0, 5)
            num_cars += random.randint(0, 4)
            num_cars += random.randint(0, 1)

        return def_pb2.SummaryResponse(num_people=num_people, num_cars=num_cars, num_trucks=num_trucks)

    def Detect(self, request_iterator, context):
        def generateRandomDetection(image):
            # generate a random detection in the image
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

        for image in request_iterator: # for each image in the stream
            ndetections = random.randint(1,3) # number of detections

            detections = def_pb2.Detections()

            # generated ndetections random detections
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
```

It defines two classes (1 for each service defined in `.proto`) and for each class 2 methods are defined (1 for each `rpc` exposed). 

When it receives a request, it generates random data (in a real world case request should be analyzed and real data should be retrieved), for example it generates random temperature measurements, random object detections, etc...

In Python, gRPC streams are supported via the usage of `yield` keyword. When `yield` is used instead of `return`, the function is called `generator`. When yield is encountered, the execution of the function stops and it returns the value following yield, for subsequent calls to the function the function execution is resumed (not restarted).

### Client implementation

The client implementation can be read in `src/client.py` but it is also provided here:


```python
import grpc

from definitions import def_pb2
from definitions import def_pb2_grpc

def image_iterator(num_frames=10):
    # generates a stream of dummy images
    for i in range(num_frames):
        yield def_pb2.Image(
            width=1920,
            height=1080,
            #image_data=...here the image should be read,
            frame_id=i
        )

def run():
    with grpc.insecure_channel('<grpc server host>:50051') as channel:
        stub = def_pb2_grpc.TemperatureSensorStub(channel)

        response_info = stub.SensorInfo(
            def_pb2.Sensor(uid = 5)
        )
        
        print('Data received from SensorInfo with Sensor(uid=5):', response_info)

        
        response_sensordata = stub.SensorData(def_pb2.Sensor(uid = 5))
        print('Data received from SensorData with Sensor(uid=5):')
        
        for data in response_sensordata: # iterating through elements of the stream
            print(data)
            

        stub2 = def_pb2_grpc.ObjectDetectionStub(channel)

        response_summary = stub2.SummaryDetection(image_iterator())
        print('Data received from SummaryDetection:', response_summary)
        
        response_detect = stub2.Detect(image_iterator())

        for detections in response_detect: # iterating throught elements of the stream
            print('Number of detection:', len(detections.list))

            for detection in detections.list: # iterating through detections in the image
                print(detection)

if __name__ == '__main__':
    run()
```

The client has local objects known as `stubs` that implements the same methods as the service. The client can then call these methods and gRPC will take care of the communication between client and server. 

