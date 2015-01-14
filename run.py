#!/usr/bin/python
import os
import sys
import signal
import argparse
import re
import subprocess
import shutil
import platform
import xml.etree.ElementTree as ET


print "running benchmarks"

def run_comand(command_list):
    env = dict(os.environ.items())
    if platform.system() == "Linux":
        env["vblank_mode"] = "0"
    p = subprocess.Popen(command_list,
                         env=env,
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE)
    (out, err) = p.communicate()
    return(out, err)

def run_synmark(test_name, result_names, result_fps):
    cur_dir = os.getcwd()

    os.chdir("../SynMark2")
    if not os.path.exists("synmark.cfg"):
        shutil.copyfile(cur_dir + "/synmark.cfg", "synmark.cfg")

    synmark = "SynMark2.exe"
    if platform.system() == "Linux":
        synmark = "./synmark2"

    (out, err) = run_comand([synmark, "-synmark", test_name])
    fps = None
    for a_line in out.splitlines():
        if a_line[:4] != "FPS:":
            continue
        tokens = a_line.split()
        fps = tokens[1]
    if fps == None:
        fps = "fail"
    result_names.append(test_name)
    result_fps.append(fps)
    os.chdir(cur_dir)

def synmark(result_names, result_fps):
    tests = ["OglBatch0",
             "OglBatch1",
             "OglBatch2",
             "OglBatch3",
             "OglBatch4",
             "OglBatch5",
             "OglBatch6",
             "OglBatch7",
             "OglCSCloth",
             "OglCSDof",
             "OglDeferred",
             "OglDeferredAA",
             "OglDrvCtx",
             "OglDrvRes",
             "OglDrvShComp",
             "OglDrvState",
             "OglFillPixel",
             "OglFillTexMulti",
             "OglFillTexSingle",
             "OglGSCloth",
             "OglGeomPoint",
             "OglGeomTriList",
             "OglGeomTriStrip",
             "OglHdrBloom",
             "OglMultithread",
             "OglOclCloth",
             "OglOclDof",
             "OglPSBump2",
             "OglPSBump8",
             "OglPSPhong",
             "OglPSPom",
             "OglShMapPcf",
             "OglShMapVsm",
             "OglTerrainFlyInst",
             "OglTerrainFlyTess",
             "OglTerrainPanInst",
             "OglTerrainPanTess",
             "OglTexFilterAniso",
             "OglTexFilterTri",
             "OglTexMem128",
             "OglTexMem512",
             "OglVSDiffuse1",
             "OglVSDiffuse8",
             "OglVSInstancing",
             "OglVSTangent",
             "OglZBuffer"]

    for atest in tests:
        run_synmark(atest, result_names, result_fps)

def run_glbench(test, test_names, test_fps):
    orig_test_name = test
    tests = {"Egypt" : "GLB27_EgyptHD_inherited_C24Z16_FixedTime",
             "Egypt_Offscreen" : "GLB27_EgyptHD_inherited_C24Z16_FixedTime_Offscreen",
             "TRex" : "GLB27_TRex_C24Z16_FixedTimeStep",
             "TRex_Offscreen" : "GLB27_TRex_C24Z16_FixedTimeStep_Offscreen"}

    dim_1080 = ["-w", "1920", "-h", "1080", "-ow", "1920", "-oh", "1080"]
    dim_720 = ["-w", "1280", "-h", "720", "-ow", "1280", "-oh", "720"]

    glbench = "GLBenchmark.exe"
    if platform.system() == "Linux":
        glbench = "./GLBenchmark"
    
    cmd = [glbench, "-skip_load_frames"]

    if "720" in test:
        cmd = cmd + dim_720
        test = test[:-3]
    else:
        cmd = cmd + dim_1080

    cur_dir = os.getcwd()
    os.chdir("../GLBenchmark")

    result_file = "data/rw/last_results_2.7.0.xml"
    if os.path.exists(result_file):
        os.unlink(result_file)
    (out, err) = run_comand(cmd + ["-t", tests[test]])
    assert(os.path.exists(result_file))
    result = ET.parse(result_file)
    fps = result.getroot().find("test_result/fps").text.split()[0]
    test_names.append(orig_test_name)
    test_fps.append(fps)
    os.chdir(cur_dir)

def glbench(test_names, test_fps):
    tests = ["TRex",
             "TRex720",
             "TRex_Offscreen",
             "Egypt",
             "Egypt720",
             "Egypt_Offscreen"]
             # "Manhattan",
             # "Manhattan_Offscreen"]

    for atest in tests:
        run_glbench(atest, test_names, test_fps)


def run_gputest(test, test_names, test_fps):
    gputest = "GpuTest.exe"
    if platform.system() == "Linux":
        gputest = "./GpuTest"
    cmd = [gputest, "/fullscreen", "/width=1920", "/height=1080", "/benchmark", 
           "/benchmark_duration_ms=10000", "/print_score", "/no_scorebox", "/test=" + test]
    cur_dir = os.getcwd()
    os.chdir("../GpuTest")
    result_file = "_geeks3d_gputest_scores.csv"
    if os.path.exists(result_file):
        os.unlink(result_file)
    (out, err) = run_comand(cmd + [test])
    assert(os.path.exists(result_file))
    lines = open(result_file).readlines()
    assert(len(lines) == 2)
    tokens = lines[0].strip().split(",")
    assert(len(tokens) == 11)   
    fps_index = None
    score_index = None
    index = 0
    for token in tokens:
        if token == "AvgFPS":
            fps_index = index
        if token == "Score":
            score_index = index
        index = index + 1
    assert(fps_index == 7)
    assert(score_index == 10)

    tokens = lines[1].strip().split(",")
    test_names.append(test + "_fps")
    test_fps.append(tokens[fps_index])

    test_names.append(test + "_score")
    test_fps.append(tokens[score_index])

    os.chdir(cur_dir)

def gputest(test_names, test_fps):
    for atest in ["fur", "pixmark_piano", "pixmark_volplosion", "plot3d", "triangle"]:
        run_gputest(atest, test_names, test_fps)
    
test_names = []
test_fps = []
gputest(test_names, test_fps)

test_names.append("blank_line")
test_fps.append("blank_line")

test_names.append("blank_line")
test_fps.append("blank_line")

test_names.append("blank_line")
test_fps.append("blank_line")

test_names.append("blank_line")
test_fps.append("blank_line")

glbench(test_names, test_fps)

test_names.append("blank_line")
test_fps.append("blank_line")

test_names.append("blank_line")
test_fps.append("blank_line")

test_names.append("blank_line")
test_fps.append("blank_line")


synmark(test_names, test_fps)
while True:
    if ! test_names:
        break
    test_name = test_names.pop(0)
    fps = test_fps.pop(0)
    print test_name + "," + fps
