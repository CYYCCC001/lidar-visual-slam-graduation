cmake_minimum_required(VERSION 3.8)
project(orb_slam3_ros2)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(OpenCV REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(Pangolin CONFIG REQUIRED
  PATHS /home/nvidia/drone/camera/orbslam3/Pangolin/build/src
  NO_DEFAULT_PATH
)

set(ORB_SLAM3_ROOT /home/nvidia/drone/camera/orbslam3/ORB_SLAM3-master)

add_executable(orb_slam3_mono
  src/orb_slam3_mono.cpp
)

target_include_directories(orb_slam3_mono PRIVATE
  ${ORB_SLAM3_ROOT}
  ${ORB_SLAM3_ROOT}/include
  ${ORB_SLAM3_ROOT}/include/CameraModels
  ${ORB_SLAM3_ROOT}/Thirdparty
  ${ORB_SLAM3_ROOT}/Thirdparty/Sophus
  ${ORB_SLAM3_ROOT}/Thirdparty/DBoW2
  ${ORB_SLAM3_ROOT}/Thirdparty/g2o
  ${EIGEN3_INCLUDE_DIRS}
)

target_link_directories(orb_slam3_mono PRIVATE
  ${ORB_SLAM3_ROOT}/lib
  ${ORB_SLAM3_ROOT}/Thirdparty/DBoW2/lib
  ${ORB_SLAM3_ROOT}/Thirdparty/g2o/lib
  /home/nvidia/drone/camera/orbslam3/Pangolin/build/src
)

target_link_libraries(orb_slam3_mono
  ORB_SLAM3
  DBoW2
  g2o
  pangolin
  ${OpenCV_LIBS}
  pthread
)

# Keep the library search path transitive for ORB-SLAM3's indirect dependencies.
target_link_options(orb_slam3_mono PRIVATE "-Wl,--disable-new-dtags")

ament_target_dependencies(orb_slam3_mono
  rclcpp
  sensor_msgs
)

set_target_properties(orb_slam3_mono PROPERTIES
  BUILD_RPATH
    "${ORB_SLAM3_ROOT}/lib;${ORB_SLAM3_ROOT}/Thirdparty/DBoW2/lib;${ORB_SLAM3_ROOT}/Thirdparty/g2o/lib;/home/nvidia/drone/camera/orbslam3/Pangolin/build/src"
  INSTALL_RPATH
    "${ORB_SLAM3_ROOT}/lib;${ORB_SLAM3_ROOT}/Thirdparty/DBoW2/lib;${ORB_SLAM3_ROOT}/Thirdparty/g2o/lib;/home/nvidia/drone/camera/orbslam3/Pangolin/build/src"
)

install(TARGETS orb_slam3_mono
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
