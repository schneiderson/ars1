# ars1

helpful tutorial for pygame:
http://thepythongamebook.com/en:pygame:step000


ToDo Stuff
- Environment
    . create environment with borders

- Robot
    . set radius
    . place in environment
    . find center
    . add sensors
    . add angle

- Kinematics (parameters are velocityLeft/velocityRight
    . test VL>VR
    . VR>VL
    . VR=VL
    . VR=0 | VL=0
    . VR>0,VL<0 | VR<0,VR>0
    . VR<0, VL<0
    . test rotation matrix
    . adjust angle

- Sensors
    . receive distance measured from center to intersection
    . adjust sensors to rotation

- ANN
    . input:
        : 12 sensor nodes
        : 2 memory nodes (velocity left and right)
    . output:
        : 2 velocities for left and right
    . activation function:
        : velocities should be just 0/1
        : discrete inner layers
        : smooth out end
        : not linear
        : flattened tanh function?

- Evolutional Network
    . fitness function
    . seed
    . iterations
    . ranking
    . dynamic delta t