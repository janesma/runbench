#!/usr/bin/python
import os, sys, signal, argparse, re, subprocess
import shutil
import xml.etree.ElementTree as ET


print "running benchmarks"

def run_comand(command_list):
    p = subprocess.Popen(command_list,
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE)
    (out, err) = p.communicate()
    return(out, err)

def run_synmark(test_name, result_dict):
    cur_dir = os.getcwd()

    os.chdir("../SynMark2")
    if not os.path.exists("synmark.cfg"):
        shutil.copyfile(cur_dir + "/synmark.cfg", "synmark.cfg")

    (out, err) = run_comand(["SynMark2.exe", "-synmark", test_name])
    fps = None
    for a_line in out.splitlines():
        if a_line[:4] != "FPS:":
            continue
        tokens = a_line.split()
        fps = tokens[1]
    result_dict[test_name] = fps
    os.chdir(cur_dir)

def synmark(result_dict):
    tests = ["OglFillPixel",
             "OglFillTexMulti",
             "OglFillTexSingle",
             "OglTexFilterAniso",
             "OglTexFilterTri",
             "OglTexMem128",
             "OglTexMem512",
             "OglGeomPoint",
             "OglGeomTriList",
             "OglGeomTriStrip",
             "OglZBuffer",
             "OglBatch0",
             "OglBatch1",
             "OglBatch2",
             "OglBatch3",
             "OglBatch4",
             "OglBatch5",
             "OglBatch6",
             "OglBatch7",
             "OglVSDiffuse1",
             "OglVSDiffuse8",
             "OglVSTangent",
             "OglVSInstancing",
             "OglPSPhong",
             "OglPSBump2",
             "OglPSBump8",
             "OglPSPom",
             "OglShMapPcf",
             "OglShMapVsm",
             "OglCSCloth",
             "OglOclCloth",
             "OglCSDof",
             "OglOclDof",
             "OglDeferred",
             "OglDeferredAA",
             "OglHdrBloom",
             "OglMultithread",
             "OglTerrainPanInst",
             "OglTerrainFlyInst",
             "OglTerrainPanTess",
             "OglTerrainFlyTess",
             "OglDrvState",
             "OglDrvShComp",
             "OglDrvRes",
             "OglDrvCtx"]

    for atest in tests:
        run_synmark(atest, result_dict)

def run_glbench(test, results):
    tests = {"Egypt" : "GLB27_EgyptHD_inherited_C24Z16_FixedTime",
             "Egypt_Offscreen" : "GLB27_EgyptHD_inherited_C24Z16_FixedTime_Offscreen",
             "TRex" : "GLB27_TRex_C24Z16_FixedTimeStep",
             "TRex_Offscreen" : "GLB27_TRex_C24Z16_FixedTimeStep_Offscreen"}

    cmd = ["GLBenchmark.exe", "-skip_load_frames", "-w", "1920", "-h", "1080", "-ow", 
           "1920", "-oh", "1080", "-t"]

    cur_dir = os.getcwd()
    os.chdir("../GLBenchMark")

    result_file = "data/rw/last_results_2.7.0.xml"
    if os.path.exists(result_file):
        os.unlink(result_file)
    (out, err) = run_comand(cmd + [tests[test]])
    assert(os.path.exists(result_file))
    result = ET.parse(result_file)
    fps = result.getroot().find("test_result/fps").text.split()[0]
    results[test] = fps
    os.chdir(cur_dir)

def glbench(results):
    tests = ["Egypt",
             "Egypt_Offscreen",
             "TRex",
             "TRex_Offscreen"]
    for atest in tests:
        run_glbench(atest, results)


def run_gputest(test, results):
    cmd = ["GpuTest.exe", "/fullscreen", "/width=1920", "/height=1080", "/benchmark", 
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
    tokens = lines[0].split(",")
    assert(len(tokens) == 11)   
    index = 0
    for token in tokens:
        if token == "AvgFPS":
            break
        index = index + 1
    assert(index == 7)

    tokens = lines[1].split(",")
    results[test] = tokens[index]
    os.chdir(cur_dir)

def gputest(results):
    for atest in ["fur", "plot3d", "triangle"]:
        run_gputest(atest, results)
    
results = {}
synmark(results)
glbench(results)
gputest(results)
for (k,v) in results.items():
    print k + ":" + v
