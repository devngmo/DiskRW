import os, sys, drwengine
os.system('@cls')

if len(sys.argv) > 1:
    testPath = sys.argv[1]
    print('Benchmark disk Read/Write at: %s' % testPath)

    if not os.path.exists(testPath):
        print('Invalid path: "%s"' % testPath)
    else:
        drwengine.testRWOnPath(testPath, 5, 50, [1024, 10240, 102400, 1024000, 10240000])