import os, sys, time, json

class DRWEngine():
    def __init__(self):
        self.testReports = {}

    def testRWOnPath(self, path, loop, files, sizes):
        self.testReports = {}
        self.testReports['Location'] = path
        self.testReports['Loop'] = loop
        self.testReports['Files'] = files

        workingDir = os.path.join(path, 'diskrw_test')
        if not os.path.exists(workingDir):
            os.mkdir(workingDir)

        finalScores = {}
        self.testReports['Final Scores'] = finalScores

        for sz in sizes:
            finalScores[sz] = { 'min': 10000, 'max':0, 'avg': 0}

        for i in range(loop):
            print('Test %d:' % (i + 1))
            writeSpeeds = self.testWriteSpeeds(workingDir, files, sizes, i == loop-1)
            self.testReports['Test %d' % i] = writeSpeeds

            for sz in sizes:
                fs = finalScores[sz]
                curTest = writeSpeeds[sz]
                if fs['min'] > curTest['min']:
                    fs['min'] = curTest['min']

                if fs['max'] < curTest['max']:
                    fs['max'] = curTest['max']

                fs['avg'] = fs['avg'] + curTest['avg']

        
        for sz in sizes:
            fs = finalScores[sz]
            fs['avg'] = fs['avg'] / loop
            kb = sz / 1024
            mb = kb / 1024
            #print(json.dumps(fs))
            mbSec = self.calcMbSec(mb, fs['min'])
            fs['Read Max Speed'] = '%.1f Mb/sec' % (mbSec)
            mbSec = self.calcMbSec(mb, fs['max'])
            fs['Read Min Speed'] = '%.1f Mb/sec' % (mbSec)
            mbSec = self.calcMbSec(mb, fs['avg'])
            fs['Read Avg Speed'] = '%.1f Mb/sec' % (mbSec)
            fs['min'] = '%.5f sec/file %d Kb' % (fs['min'], sz/1024)
            fs['max'] = '%.5f sec/file %d Kb' % (fs['max'], sz/1024)
            fs['avg'] = '%.5f sec/file %d Kb' % (fs['avg'], sz/1024)
            #readSpeeds = self.testReadSpeed(workingDir, files, sizes)
            #self.testReports['Test %d Write speed' % i] = readSpeeds
    def calcMbSec(self, mb, sec):
        return mb / sec

    def testWriteSpeeds(self, workingDir, files, sizes, cleanup = False):
        writeSpeeds = {}
        # clean up
        print('Cleanup...')
        fpList = []
        nFileRemoved = 0
        
        for sz in sizes:
            for i in range(files):
                fp = os.path.join(workingDir, '_%d_%d.bin' % (sz, i))
                if os.path.exists(fp):
                    os.remove(fp)
                    nFileRemoved = nFileRemoved + 1
        print('    %d file removed.' % nFileRemoved)

        for sz in sizes:
            szSpeeds = {}
            speedList = []
            buffer = self.createBuffer(sz)
            for i in range(files):
                fp = os.path.join(workingDir, '_%d_%d.bin' % (sz, i))
                start = time.time()
                f = open(fp, 'wb')
                f.write(buffer)
                f.close()
                end = time.time()
                oneFileSpeed = end - start # seconds
                if oneFileSpeed == 0:
                    oneFileSpeed = 0.00001
                speedList = speedList + [oneFileSpeed]
            szSpeeds['list'] = speedList
            szSpeeds['min'] = self.listMin(speedList)
            szSpeeds['max'] = self.listMax(speedList)
            szSpeeds['avg'] = self.listAvg(speedList)

            writeSpeeds[sz] = szSpeeds

        nFileRemoved = 0
        if cleanup:
            for sz in sizes:
                for i in range(files):
                    fp = os.path.join(workingDir, '_%d_%d.bin' % (sz, i))
                    if os.path.exists(fp):
                        os.remove(fp)
                        nFileRemoved = nFileRemoved + 1
            print('    %d file removed.' % nFileRemoved)
        return writeSpeeds

    def listMin(self, ls):
        min = ls[0]
        for a in ls:
            if min > a:
                min = a
        return min

    def listMax(self, ls):
        max = ls[0]
        for a in ls:
            if max < a:
                max = a
        return max

    def listAvg(self, ls):
        avg = 0
        for a in ls:
            avg = avg + a
        return avg / len(ls)

    def createBuffer(self, sz):
        arr = bytearray(sz)
        return arr
            
    def printReport(self):
        print('=================================================')
        print('Benchmark Report')
        print('=================================================')
        info = self.testReports['Final Scores']
        print('%s' % ( json.dumps(info, indent = 2) ))

def testRWOnPath(path, loop, files, sizes):
    e = DRWEngine()
    e.testRWOnPath(path, loop, files, sizes)
    e.printReport()