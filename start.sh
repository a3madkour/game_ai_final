#!/bin/bash
java -cp jar/FightingICE.jar:lib/javax.json-1.0.4.jar:lib/py4j0.10.4.jar:lib/lwjgl/lwjgl-glfw.jar:lib/lwjgl/lwjgl.jar:lib/lwjgl/lwjgl-openal.jar:lib/lwjgl/lwjgl-opengl.jar:lib/lwjgl/lwjgl_util.jar:lib/natives/linux/lwjgl-glfw-natives-linux.jar:lib/natives/linux/lwjgl-natives-linux.jar:lib/natives/linux/lwjgl-openal-natives-linux.jar:lib/natives/linux/lwjgl-opengl-natives-linux.jar Main --py4j --black-bg --port 4242

