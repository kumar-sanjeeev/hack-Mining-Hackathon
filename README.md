# Hack-Mining-Hackathon
This repository contains code files, problem statement, pitch deck and final result, that we in a team had developed in 
[**Hack-Mining**](https://hackmining.github.io/) hackathon organized by RWTH and VDMA from `fri-sun 07-09 oct 2022`.

## Problem Statement: 
### `PosSys 4.0 - 2D position detection system` by [Becker Mining Systems](https://www.becker-mining.com/)

A new Becker product **`PDS 4.0`** is about to reach production phase:

#### About PDS 4.0:
    
  - It is collision awareness and proximity detection system.The goal of the system is to prevent accidents in mining operations between vehicles and 
    between vehicles and mining personnel. For this purpose it will be mounted on mining 
    vehicles and feature Tags for mining  personnel. The system will constantly measure the 
    distance between all detectable participants and be able to interact with the vehicles and be 
    able to engage breaks or slow down the vehicle in dangerous situations, which otherwise 
    could end deadly. 
    
 **For the purpose of evaluating the reliability and accuracy of the PDS 4.0 a way of measuring needs to 
be established**

#### PosSys4.0 Overview:

  - The same ranging technology being utilized in the PDS4.0 should be used in PosSys4.0.An API for interacting with the distance measuring chip (Nanotron Swarmbee) is provided. 
    Trilateration as mathematical foundation turns the distances to positions. 
  - Requirement about deployment:
      - Deployment of the system must be fast
      - Coordinate System setup simple usage 
      
      
 ## Our Result:
 
 **Explanation:**
 
 - Red cross represents the anchors that has been placed in triangle position
 - Blue ellipse represent the target that has been moving in between anchors, varying ellipse size represent the circle of uncertainity in the positin of target.
 
 ![imgs](https://user-images.githubusercontent.com/62834697/195923153-bb10e67b-1147-44f7-b386-1e66a4e19c40.gif)
