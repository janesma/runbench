#!/usr/bin/python
import os
import subprocess
import shutil
import platform
import time
import xml.etree.ElementTree as ET


print "running benchmarks"

def run_comand(command_list, ld_path=None, add_env=None):
    time.sleep(2)
    env = dict(os.environ.items())
    if platform.system() == "Linux":
        env["vblank_mode"] = "0"
        # for gfxbench
        if ld_path and not "LD_LIBRARY_PATH" in env:
            env["LD_LIBRARY_PATH"] = ""
        if ld_path:
            env["LD_LIBRARY_PATH"] = env["LD_LIBRARY_PATH"] + ":" + ld_path

        if add_env:
            for (k,v) in add_env.items():
                env[k] = v        
            
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

    synmark_exe = "SynMark2.exe"
    if platform.system() == "Linux":
        synmark_exe = "./synmark2"

    (out, _) = run_comand([synmark_exe, "-synmark", test_name])
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
             "OglDeferred",
             "OglDeferredAA",
             "OglFillPixel",
             "OglFillTexMulti",
             "OglFillTexSingle",
             "OglGeomPoint",
             "OglGeomTriList",
             "OglGeomTriStrip",
             "OglHdrBloom",
             "OglMultithread",
             "OglPSBump2",
             "OglPSBump8",
             "OglPSPhong",
             "OglPSPom",
             "OglShMapPcf",
             "OglShMapVsm",
             "OglTerrainFlyInst",
             "OglTerrainPanInst",
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

    glbench_exe = "GLBenchmark.exe"
    if platform.system() == "Linux":
        glbench_exe = "./GLBenchmark"
    
    cmd = [glbench_exe, "-skip_load_frames"]

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
    run_comand(cmd + ["-t", tests[test]])
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


def run_gfxbench(atest, result_names, result_fps):
    if platform.system() != "Linux":
        result_names.append("atest")
        result_fps.append("not run")
    cur_dir = os.getcwd()
    os.chdir("../gfxbench/out/build/linux/gfxbench_Release/mainapp")
    ld_path = os.path.abspath("../../../../install/linux/lib")

    add_env = {"MESA_GL_VERSION_OVERRIDE" : "4.1",
               "MESA_GLSL_VERSION_OVERRIDE" :"400" }

    cmd =  ["./mainapp", "-w", "1920", "-h", "1080", "-t", atest]
    (out, _) = run_comand(cmd, ld_path=ld_path, add_env=add_env)
    for aline in out:
        if "fps" not in aline:
            continue
        tokens = aline.strip().split(":")
        result_fps.append(tokens[1].strip())
        result_names.append(atest)
        return
    os.chdir(cur_dir)
        
def gfxbench(test_names, test_fps):
    tests = ["gl_manhattan", "gl_manhattan_off"]
    for atest in tests:
        run_gfxbench(atest, test_names, test_fps)

def run_gputest(test, test_names, test_fps):
    gputest_exe = "GpuTest.exe"
    if platform.system() == "Linux":
        gputest_exe = "./GpuTest"
    cmd = [gputest_exe, "/fullscreen", "/width=1920", "/height=1080", "/benchmark", 
           "/benchmark_duration_ms=10000", "/print_score", "/no_scorebox", "/test=" + test]
    cur_dir = os.getcwd()
    os.chdir("../GpuTest")
    result_file = "_geeks3d_gputest_scores.csv"
    if os.path.exists(result_file):
        os.unlink(result_file)
    run_comand(cmd + [test])
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
    for atest in ["fur", "pixmark_piano", "pixmark_volplosion", "plot3d"]:
        run_gputest(atest, test_names, test_fps)
    
_test_names = []
_test_fps = []

gputest(_test_names, _test_fps)

_test_names.append("blank_line")
_test_fps.append("blank_line")

_test_names.append("blank_line")
_test_fps.append("blank_line")

_test_names.append("blank_line")
_test_fps.append("blank_line")

_test_names.append("blank_line")
_test_fps.append("blank_line")

glbench(_test_names, _test_fps)

gfxbench(_test_names, _test_fps)

_test_names.append("blank_line")
_test_fps.append("blank_line")

synmark(_test_names, _test_fps)
while True:
    if not _test_names:
        break
    _test_name = _test_names.pop(0)
    _fps = _test_fps.pop(0)
    print _test_name + "," + _fps
