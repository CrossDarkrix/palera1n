import argparse, ast, json, os, platform, re, shutil, subprocess, sys, tarfile, threading, time, urllib.request, zipfile
from datetime import datetime
from io import BytesIO
try:
    import colorama
except:
    print('Colorama not Installed!Auto installing...')
    subprocess.run('{} -m pip install -U colorama'.format(sys.executable), shell=True)
    import colorama
import logging
logger = logging.getLogger("palera1n")

colorama.init()

ipsw = [''] # IF YOU WERE TOLD TO PUT A CUSTOM IPSW URL, PUT IT HERE. YOU CAN FIND THEM ON https://appledb.dev
ipsw_url = ['']
version = '1.3.0_py'
OS_Type = platform.system()
rootpath = os.getcwd()
Dir = os.path.join(os.getcwd(), 'binaries', OS_Type)
commit = subprocess.Popen('git rev-parse --short HEAD', shell=True, stdout=subprocess.PIPE).communicate()[0].decode()
branch = subprocess.Popen('git rev-parse --abbrev-ref HEAD', shell=True, stdout=subprocess.PIPE).communicate()[0].decode()
LogFileName = '{}-{}-{}.log'.format(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'), platform.system(), platform.release())

Tweaks = ['0']
_Tweaks = ['0']
Semi_tethered = ['0']
Dfuhelper = ['0']
Skip_fakefs = ['0']
No_baseband = ['0']
No_install = ['0']
Verbose = ['0']
Restorerootfs = ['0']
Force_CreateFakeFS = ['0']
Debug = ['0']
Clean = ['0']
Device_Mode = ['']
DeviD = ['']
PyIMG4Check = ['0']
Default_Disk = ['8']

# Logger
class SaveLogger:
    def __init__(self, FName):
        self.Console = sys.__stdout__
        self.File = open(FName, 'w', encoding='utf-8')

    def write(self, message):
        self.Console.write(message)
        self.File.write(message)

    def flush(self):
        self.Console.flush()
        self.File.flush()

# Functions
def Remote_cmd(cmd):
    subprocess.run('{} -p "alpine" ssh -o StrictHostKeyChecking=no -p2222 root@localhost "{}"'.format(os.path.join(Dir, 'sshpass'), cmd), shell=True)

def Remote_cmd2(cmd):
    out, err = subprocess.Popen('{} -p "alpine" ssh -o StrictHostKeyChecking=no -p2222 root@localhost "{}"'.format(os.path.join(Dir, 'sshpass'), cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    outs = out.decode()
    errs = err.decode()
    if not outs == '':
        return outs
    elif not errs == '':
        return errs

def Remote_cp(cmd):
    subprocess.run('{} -p "alpine" scp -o StrictHostKeyChecking=no -P2222 {}'.format(os.path.join(Dir, 'sshpass'), cmd), shell=True)

def Step(num, message):
    for i in reversed(range(0, num)):
        print(colorama.Fore.CYAN + '({}) {}'.format(message, i), end='\r', flush=True)
        time.sleep(0.9)
    print('{} (0)\n'.format(message), end='\r', flush=True)
    print(colorama.Fore.RESET)

def Recovery_Fix_Auto_Boot():
    if Tweaks[0] == '1':
        subprocess.run('{} -c "setenv auto-boot false"'.format(os.path.join(Dir, 'irecovery')), shell=True)
        subprocess.run('{} -c "saveenv"'.format(os.path.join(Dir, 'irecovery')), shell=True)
    else:
        subprocess.run('{} -c "setenv auto-boot true"'.format(os.path.join(Dir, 'irecovery')), shell=True)
        subprocess.run('{} -c "saveenv"'.format(os.path.join(Dir, 'irecovery')), shell=True)
    if Semi_tethered[0] == '1':
        subprocess.run('{} -c "setenv auto-boot true"'.format(os.path.join(Dir, 'irecovery')), shell=True)
        subprocess.run('{} -c "saveenv"'.format(os.path.join(Dir, 'irecovery')), shell=True)

def _Info(argm, sed):
    if argm == 'recovery':
        try:
            devinfo = re.search('({}:) (.+)'.format(sed), subprocess.Popen('{} -q'.format(os.path.join(Dir, 'irecovery')), shell=True, stdout=subprocess.PIPE).communicate()[0].decode()).group(2)
        except:
            devinfo = ''
    elif argm == 'normal':
        try:
            devinfo = re.search('({}:) (.+)'.format(sed), subprocess.Popen('{}'.format(os.path.join(Dir, 'ideviceinfo')), shell=True, stdout=subprocess.PIPE).communicate()[0].decode()).group(2)
        except:
            devinfo = ''
    print(devinfo)
    return devinfo

def _Pwn():
    pwnd = _Info('recovery', 'PWND')
    if pwnd == "":
        print('[*] Pwning device')
        subprocess.run('{} pwn'.format(os.path.join(Dir, 'gaster')), shell=True)
        time.sleep(1.9)

def _Reset():
    print('[*] Resetting DFU state')
    subprocess.run('{} reset'.format(os.path.join(Dir, 'gaster')), shell=True)

def Get_Device_Mode():
    if OS_Type == 'Darwin':
        _Appl = re.findall('(?<= ID: ).+', subprocess.Popen('system_profiler SPUSBDataType', shell=True, stdout=subprocess.PIPE).communicate()[0].decode())
        apples = [_Appl[i-1].split('x')[1] for i, x in enumerate(_Appl) if '0x05ac' in x]
    elif OS_Type == 'Linux':
        _Appl = '\n'.join(x for x in subprocess.Popen('lsusb', shell=True, stdout=subprocess.PIPE).communicate()[0].decode().split('\n') if '05ac:' in x)
        apples = [xx.split(' ')[5].split(':')[1] for xx in _Appl.split('\n')]
    dev_count = 0
    for apple_device in apples:
        if apple_device == '12ab':
            Device_Mode[0] = 'normal'
            dev_count += 1
        if apple_device == '12a8':
            Device_Mode[0] = 'normal'
            dev_count += 1
        if apple_device == '1281':
            Device_Mode[0] = 'recovery'
            dev_count += 1
        if apple_device == '1227':
            Device_Mode[0] = 'dfu'
            dev_count += 1
        if apple_device == '1222':
            Device_Mode[0] = 'diag'
            dev_count += 1
        if apple_device == '1338':
            Device_Mode[0] = 'checkra1n_stage2'
            dev_count += 1
        if apple_device == '4141':
            Device_Mode[0] = 'pongo'
            dev_count += 1
    if dev_count == 0:
        Device_Mode[0] = 'none'
    elif 2 <= dev_count:
        raise '[-] Please attach only one device'
    if OS_Type == 'Linux':
        try:
            if 'ramdisk tool' in re.search('ramdisk tool (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) [0-9]{1,2} [0-9]{1,4} [0-9]{2}:[0-9]{2}:[0-9]{2}', re.search('.*(\n{1})', subprocess.Popen('cat /sys/bus/usb/devices/*/serial', shell=True, stdout=subprocess.PIPE).communicate()[0].decode()).group().split('\n')[0]).group():
                Device_Mode[0] = 'ramdisk'
        except:
            pass
    elif OS_Type == 'Darwin':
        try:
            if 'ramdisk tool' in re.search('ramdisk tool (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) [0-9]{1,2} [0-9]{1,4} [0-9]{2}:[0-9]{2}:[0-9]{2}', re.search('(Serial Number).*', subprocess.Popen('system_profiler SPUSBDataType', shell=True, stdout=subprocess.PIPE).communicate()[0].decode()).group().split(': ')[1]).group():
                Device_Mode[0] = 'ramdisk'
        except:
            pass
    print(Device_Mode[0])
    return Device_Mode[0]

def _Wait(cmd):
    if (Get_Device_Mode() != cmd):
        print('[*] Waiting for device in {} mode'.format(cmd))
    while (Get_Device_Mode() != cmd):
        time.sleep(1)
    if cmd == 'recovery':
        Recovery_Fix_Auto_Boot()

def BackSleepStep():
    Step(4, StepOne)

def _DFUHelper(device):
    global StepOne
    device_iD = _Info('normal', 'ProductType')
    if re.compile('0x801.*').search(device) and not re.compile('.*iPad.*').search(device_iD):
        StepOne = 'Hold volume down + side button'
    else:
        StepOne = 'Hold home + power button'
    input('[*] Press Return / Enter key when ready for DFU mode')
    Step(3, 'Get Ready')
    threading.Thread(target=BackSleepStep, daemon=True).start()
    time.sleep(2.9)
    subprocess.run('{} -c "reset"'.format(os.path.join(Dir, 'irecovery')), shell=True)
    Step(1, 'Keep holding')
    if re.compile('0x801.*').search(device) and not re.compile('.*iPad.*').search(device_iD):
        Step(10, 'Release side button, but keep holding volume down')
    else:
        Step(10, 'Release power button, but keep holding home button')
    time.sleep(0.9)
    if Get_Device_Mode() == 'dfu':
        print('[*] Device entered DFU!')
        return 0
    else:
        print('[-] Device did not enter DFU mode, rerun the script and try again')
        return -1

def _Kill_If_Running(process):
    if not subprocess.Popen('pgrep -u root -xf "{}"'.format(process), shell=True, stdout=subprocess.PIPE).communicate()[0].decode() == '':
        subprocess.run('sudo killall {}'.format(process), shell=True)
    else:
        if not subprocess.Popen('pgrep -x "{}"'.format(process), shell=True, stdout=subprocess.PIPE).communicate()[0].decode() == '':
            subprocess.run('killall {}'.format(process), shell=True)

def _Exit_Handler():
    if OS_Type == 'Darwin':
        subprocess.run('defaults write -g ignore-devices -bool false', shell=True)
        subprocess.run('defaults write com.apple.AMPDevicesAgent dontAutomaticallySyncIPods -bool false', shell=True)
        subprocess.run('killall Finder', shell=True)
    os.chdir(os.path.join(rootpath, 'logs'))
    for files in sorted(os.listdir()):
        if files.split('.')[1].lower() == 'log':
            if files == LogFileName:
                os.rename(files, 'FAIL_{}'.format(files))
                break
    print("[*] A failure log has been made. If you're going to make a GitHub issue, please attach the latest log.")
    sys.exit(1)

def RootStartiProxy():
    subprocess.run('sudo {} -2222 22'.format(os.path.join(Dir, 'iproxy')), shell=True)

def StartiProxy():
    subprocess.run('{} -2222 22'.format(os.path.join(Dir, 'iproxy')), shell=True)

def KernelDiFF(Original, Patched, arg3):
    SizeP = os.path.getsize(Patched)
    SizeO = os.path.getsize(Original)
    if SizeP != SizeO:
        raise "size does not match, can't compare files! exiting..."
    pd = open(Patched, 'rb').read()
    od = open(Original, 'rb').read()
    A = 0
    Diff = []
    with open(arg3, 'w+') as DiffFile:
        DiffFile.write('#AMFI\n\n')
        for d in range(SizeO):
            OriginalBytes = od[d]
            PatchedBytes = pd[d]
            if OriginalBytes != PatchedBytes:
                if A == 1e6:
                    for dd in Diff:
                        data = '{} {} {}\n'.format(dd[0], dd[1], dd[2])
                        DiffFile.write(data)
                    Diff = []
                    A = 0
                Diff.append([hex(d), hex(OriginalBytes), hex(PatchedBytes)])
                A += 1
        for dd2 in Diff:
            data2 = '{} {} {}\n'.format(dd2[0], dd2[1], dd2[2])
            DiffFile.write(data2)

def SSHRD(arg, arg2='', arg3=''):
    sshrd_work_dir = os.path.join(rootpath, 'ramdisk')
    sshrd_gaster_download_check = '0'
    if OS_Type == 'Darwin':
        sshrd_gaster_download_check = '1'
    if OS_Type == 'Linux':
        sshrd_gaster_download_check = '1'
    if OS_Type == 'Windows':
        raise 'Unsupported OS Detected!\nExiting.....'
    if sshrd_gaster_download_check == '1':
        if not os.path.exists(os.path.join(OS_Type, 'gaster')):
            gaster_URL = 'https://nightly.link/palera1n/gaster/workflows/makefile/main/gaster-{}.zip'.format(OS_Type)
            print('[*] Downloading gaster.....')
            gaster_Data = urllib.request.urlopen(urllib.request.Request(gaster_URL, headers={'User-Agent': 'curl/7.85.0'})).read()
            with zipfile.ZipFile(BytesIO(gaster_Data), 'r') as gaster_zip:
                gaster_zip.extractall(OS_Type+'/.')
            print('[*] gaster Download Done!')
    BackPath = os.getcwd()
    os.chdir(os.path.join(sshrd_work_dir, OS_Type))
    for chFile in sorted(os.listdir()):
        try:
            os.chmod(chFile, 0o755)
        except:
            pass
    os.chdir(BackPath)
    Ipsw_URL = ipsw_url[0]
    Check = _Info('recovery', 'CPID')
    Replace = _Info('recovery', 'MODEL')
    Device_iD = _Info('recovery', 'PRODUCT')
    Dev_Check = '0'
    if OS_Type == 'Darwin':
        if not re.compile('.+(DFU Mode).+').search(subprocess.Popen('system_profiler SPUSBDataType 2> /dev/null', shell=True, stdout=subprocess.PIPE).communicate()[0].decode()):
            print("[*] Waiting for device in DFU mode")
        while not re.compile('.+(DFU Mode).+').search(subprocess.Popen('system_profiler SPUSBDataType 2> /dev/null', shell=True, stdout=subprocess.PIPE).communicate()[0].decode()):
            time.sleep(0.9)
    elif OS_Type == 'Linux':
        if not re.compile('.+(DFU Mode).+').search(subprocess.Popen('lsusb 2> /dev/null', shell=True, stdout=subprocess.PIPE).communicate()[0].decode()):
            print("[*] Waiting for device in DFU mode")
        while not re.compile('.+(DFU Mode).+').search(subprocess.Popen('lsusb 2> /dev/null', shell=True, stdout=subprocess.PIPE).communicate()[0].decode()):
            time.sleep(0.9)
    if os.path.exists('work'):
        shutil.rmtree('work')
    os.makedirs('sshramdisk', exist_ok=True)
    if arg == 'boot':
        if not os.path.exists(os.path.join('sshramdisk', 'iBSS.img4')):
            raise "[-] Please create an SSH ramdisk first!"
        subprocess.run('{} pwn'.format(os.path.join(sshrd_work_dir, OS_Type, 'gaster')), shell=True)
        subprocess.run('{} reset'.format(os.path.join(sshrd_work_dir, OS_Type, 'gaster')), shell=True)
        subprocess.run('{} -f sshramdisk/iBSS.img4'.format(os.path.join(sshrd_work_dir, OS_Type, 'irecovery')), shell=True)
        time.sleep(1.9)
        subprocess.run('{} -f sshramdisk/iBEC.img4'.format(os.path.join(sshrd_work_dir, OS_Type, 'irecovery')), shell=True)
        if Check == '0x8010':
            Dev_Check = '1'
        if Check == '0x8015':
            Dev_Check = '1'
        if Check == '0x8010':
            Dev_Check = '1'
        if Check == '0x8011':
            Dev_Check = '1'
        if Check == '0x8012':
            Dev_Check = '1'
        if Dev_Check == '1':
            subprocess.run('{} -c go'.format(os.path.join(sshrd_work_dir, OS_Type, 'irecovery')), shell=True)
            time.sleep(4.9)
        else:
            subprocess.run('{} -f sshramdisk/iBEC.img4'.format(os.path.join(sshrd_work_dir, OS_Type, 'irecovery')), shell=True)
            time.sleep(4.9)
        subprocess.run('{} -f sshramdisk/bootlogo.img4'.format(os.path.join(sshrd_work_dir, OS_Type, 'irecovery')), shell=True)
        time.sleep(0.9)
        subprocess.run('{} -c "setpicture 0x1"'.format(os.path.join(sshrd_work_dir, OS_Type, 'irecovery')), shell=True)
        time.sleep(0.9)
        subprocess.run('{} -f sshramdisk/ramdisk.img4'.format(os.path.join(sshrd_work_dir, OS_Type, 'irecovery')), shell=True)
        time.sleep(0.9)
        subprocess.run('{} -c ramdisk'.format(os.path.join(sshrd_work_dir, OS_Type, 'irecovery')), shell=True)
        time.sleep(0.9)
        subprocess.run('{} -f sshramdisk/devicetree.img4'.format(os.path.join(sshrd_work_dir, OS_Type, 'irecovery')), shell=True)
        time.sleep(0.9)
        subprocess.run('{} -c devicetree'.format(os.path.join(sshrd_work_dir, OS_Type, 'irecovery')), shell=True)
        time.sleep(0.9)
        subprocess.run('{} -f sshramdisk/trustcache.img4'.format(os.path.join(sshrd_work_dir, OS_Type, 'irecovery')), shell=True)
        time.sleep(0.9)
        subprocess.run('{} -c firmware'.format(os.path.join(sshrd_work_dir, OS_Type, 'irecovery')), shell=True)
        time.sleep(0.9)
        subprocess.run('{} -f sshramdisk/kernelcache.img4'.format(os.path.join(sshrd_work_dir, OS_Type, 'irecovery')), shell=True)
        time.sleep(0.9)
        subprocess.run('{} -c bootx'.format(os.path.join(sshrd_work_dir, OS_Type, 'irecovery')), shell=True)
    if arg == '':
        raise "1st argument: iOS version for the ramdisk\n"
    os.makedirs('work', exist_ok=True)
    subprocess.run('{} pwn'.format(os.path.join(sshrd_work_dir, OS_Type, 'gaster')), shell=True)
    subprocess.run('{} -e -s shsh/"{}.shsh" -m work/IM4M'.format(os.path.join(sshrd_work_dir, OS_Type, 'img4tool'), Check), shell=True)
    os.chdir(os.path.join(sshrd_work_dir, 'work'))
    os.makedirs('Firmware/all_flush', exist_ok=True)
    subprocess.run('{} -g BuildManifest.plist "{}"'.format(os.path.join(sshrd_work_dir, OS_Type, 'pzb'), Ipsw_URL), shell=True)
    BuildManifest = open('BuildManifest.plist', 'rb').read().decode()
    subprocess.run('{} -g "{}" "{}"'.format(os.path.join(sshrd_work_dir, OS_Type, 'pzb'), re.sub('<.*?[string]>', '', re.search('.+[{}].*iBSS[.].*'.format(Replace), BuildManifest).group()).replace('\t',''), Ipsw_URL), shell=True)
    subprocess.run('{} -g "{}" "{}"'.format(os.path.join(sshrd_work_dir, OS_Type, 'pzb'), re.sub('<.*?[string]>', '', re.search('.+[{}].*iBEC[.].*'.format(Replace), BuildManifest).group()).replace('\t',''), Ipsw_URL), shell=True)
    subprocess.run('{} -g "{}" "{}"'.format(os.path.join(sshrd_work_dir, OS_Type, 'pzb'), re.sub('<.*?[string]>', '', re.search('.+[{}].*DeviceTree[.].*'.format(Replace), BuildManifest).group()).replace('\t',''), Ipsw_URL), shell=True)
    if OS_Type == 'Darwin':
        subprocess.run('{} -g Firmware/"{}".trustcache "{}"'.format(os.path.join(sshrd_work_dir, OS_Type, 'pzb'), re.sub('<.*?[string]>', '', re.search('<.*?[string]>(.+)<.*?[string]>', subprocess.Popen('/usr/bin/plutil -extract "BuildIdentities".0."Manifest"."RestoreRamDisk"."Info"."Path" xml1 -o - BuildManifest.plist', shell=True, stdout=subprocess.PIPE).communicate()[0].decode()).group()).replace('\n',''), Ipsw_URL), shell=True)
    elif OS_Type == 'Linux':
        subprocess.run('{} -g Firmware/"{}".trustcache "{}"'.format(os.path.join(sshrd_work_dir, OS_Type, 'pzb'), subprocess.Popen('{} BuildManifest.plist -c "Print BuildIdentities:0:Manifest:RestoreRamDisk:Info:Path"'.format(os.path.join(sshrd_work_dir, OS_Type, 'PlistBuddy')), shell=True, stdout=subprocess.PIPE).communicate()[0].decode().replace('"', ''), Ipsw_URL), shell=True)
    subprocess.run('{} -g "{}" "{}"'.format(os.path.join(sshrd_work_dir, OS_Type, 'pzb'), re.sub('<.*?[string]>', '', re.search('.*kernelcache.release[.].*', BuildManifest).group()).replace('\t',''), Ipsw_URL), shell=True)
    if OS_Type == 'Darwin':
        subprocess.run('{} -g "{}" "{}"'.format(os.path.join(sshrd_work_dir, OS_Type, 'pzb'), re.sub('<.*?[string]>', '', re.search('<.*?[string]>(.+)<.*?[string]>', subprocess.Popen('/usr/bin/plutil -extract "BuildIdentities".0."Manifest"."RestoreRamDisk"."Info"."Path" xml1 -o - BuildManifest.plist', shell=True, stdout=subprocess.PIPE).communicate()[0].decode()).group()).replace('\n',''), Ipsw_URL), shell=True)
    elif OS_Type == 'Linux':
        subprocess.run('{} -g "{}" "{}"'.format(os.path.join(sshrd_work_dir, OS_Type, 'pzb'), subprocess.Popen('{} BuildManifest.plist -c "Print BuildIdentities:0:Manifest:RestoreRamDisk:Info:Path"'.format(os.path.join(sshrd_work_dir, OS_Type, 'PlistBuddy')), shell=True, stdout=subprocess.PIPE).communicate()[0].decode().replace('"', ''), Ipsw_URL), shell=True)
    os.chdir(sshrd_work_dir)
    BuildManifest2 = open('work/BuildManifest.plist', 'rb').read().decode()
    subprocess.run('{} decrypt work/"{}" work/iBSS.dec'.format(os.path.join(sshrd_work_dir, OS_Type, 'gaster'), re.sub('<.*?[string]>', '', re.search('.+[{}].*iBSS[.].*'.format(Replace), BuildManifest2).group()).replace('\t','').split('/')[2]), shell=True)
    subprocess.run('{} decrypt work/"{}" work/iBEC.dec'.format(os.path.join(sshrd_work_dir, OS_Type, 'gaster'), re.sub('<.*?[string]>', '', re.search('.+[{}].*iBEC[.].*'.format(Replace), BuildManifest2).group()).replace('\t','').split('/')[2]), shell=True)
    subprocess.run('{} work/iBSS.dec work/iBSS.patched'.format(os.path.join(sshrd_work_dir, OS_Type, 'iBoot64Patcher')), shell=True)
    subprocess.run('{} -i work/iBSS.patched -o sshramdisk/iBSS.img4 -M work/IM4M -A -T ibss'.format(os.path.join(sshrd_work_dir, OS_Type, 'img4')), shell=True)
    subprocess.run('{} work/iBEC.dec work/iBEC.patched -b "rd=md0 debug=0x2014e wdt=-1 `if [ -z "$2" ]; then :; else echo "$2=$3"; fi` `if [ "$check" = "0x8960" ] || [ "$check" = "0x7000" ] || [ "$check" = "0x7001" ]; then echo "-restore"; fi`" -n'.format(os.path.join(sshrd_work_dir, OS_Type, 'iBoot64Patcher')), shell=True)
    subprocess.run('{} -i work/iBEC.patched -o sshramdisk/iBEC.img4 -M work/IM4M -A -T ibec'.format(os.path.join(sshrd_work_dir, OS_Type, 'img4')), shell=True)
    subprocess.run('{} -i work/"{}" -o work/kcache.raw'.format(os.path.join(sshrd_work_dir, OS_Type, 'img4'), re.sub('<.*?[string]>', '', re.search('.*kernelcache.release[.].*', BuildManifest2).group()).replace('\t','')), shell=True)
    subprocess.run('{} work/kcache.raw work/kcache.patched -a'.format(os.path.join(sshrd_work_dir, OS_Type, 'Kernel64Patcher')), shell=True)
    KernelDiFF('work/kcache.raw', 'work/kcache.patched', 'work/kc.bpatch')
    subprocess.run('{} -i work/"{}" -o sshramdisk/kernelcache.img4 -M work/IM4M -T rkrn -P work/kc.bpatch `if [ "$oscheck" = "Linux" ]; then echo "-J"; fi`'.format(os.path.join(sshrd_work_dir, OS_Type, 'img4'), re.sub('<.*?[string]>', '', re.search('.*kernelcache.release[.].*', BuildManifest2).group()).replace('\t','')), shell=True)
    subprocess.run('{} -i work/"{}" -o sshramdisk/devicetree.img4 -M work/IM4M -T rdtr'.format(os.path.join(sshrd_work_dir, OS_Type, 'img4'), re.sub('<.*?[string]>', '', re.search('.+[{}].*DeviceTree[.].*'.format(Replace), BuildManifest2).group()).replace('\t','')), shell=True)
    if OS_Type == 'Darwin':
        subprocess.run('{} -i work/"{}".trustcache -o sshramdisk/trustcache.img4 -M work/IM4M -T rtsc'.format(os.path.join(sshrd_work_dir, OS_Type, 'img4'), re.sub('<.*?[string]>', '', re.search('<.*?[string]>(.+)<.*?[string]>', subprocess.Popen('/usr/bin/plutil -extract "BuildIdentities".0."Manifest"."RestoreRamDisk"."Info"."Path" xml1 -o - BuildManifest.plist', shell=True, stdout=subprocess.PIPE).communicate()[0].decode()).group()).replace('\n','')), shell=True)
        subprocess.run('{} -i work/"{}" -o work/ramdisk.dmg'.format(os.path.join(sshrd_work_dir, OS_Type, 'img4'), re.sub('<.*?[string]>', '', re.search('<.*?[string]>(.+)<.*?[string]>', subprocess.Popen('/usr/bin/plutil -extract "BuildIdentities".0."Manifest"."RestoreRamDisk"."Info"."Path" xml1 -o - BuildManifest.plist', shell=True, stdout=subprocess.PIPE).communicate()[0].decode()).group()).replace('\n','')), shell=True)
    elif OS_Type == 'Linux':
        subprocess.run('{} -i work/"{}".trustcache -o sshramdisk/trustcache.img4 -M work/IM4M -T rtsc'.format(os.path.join(sshrd_work_dir, OS_Type, 'img4'), subprocess.Popen('{} BuildManifest.plist -c "Print BuildIdentities:0:Manifest:RestoreRamDisk:Info:Path"'.format(os.path.join(sshrd_work_dir, OS_Type, 'PlistBuddy')), shell=True, stdout=subprocess.PIPE).communicate()[0].decode().replace('"', '')), shell=True)
        subprocess.run('{} -i work/"{}" -o work/ramdisk.dmg'.format(os.path.join(sshrd_work_dir, OS_Type, 'img4'), subprocess.Popen('{} BuildManifest.plist -c "Print BuildIdentities:0:Manifest:RestoreRamDisk:Info:Path"'.format(os.path.join(sshrd_work_dir, OS_Type, 'PlistBuddy')), shell=True, stdout=subprocess.PIPE).communicate()[0].decode().replace('"', '')), shell=True)
    if OS_Type == 'Darwin':
        subprocess.run('hdiutil resize -size 256MB work/ramdisk.dmg', shell=True)
        subprocess.run('hdiutil attach -mountpoint /tmp/SSHRD work/ramdisk.dmg', shell=True)
        subprocess.run('{} -x --no-overwrite-dir -f other/ramdisk.tar.gz -C /tmp/SSHRD/'.format(os.path.join(sshrd_work_dir, OS_Type, 'gtar')), shell=True)
        if not arg2 == 'rootless':
            PogoZip = urllib.request.urlopen(urllib.request.Request('https://nightly.link/elihwyma/Pogo/workflows/build/root/Pogo.zip', headers={'User-Agent': 'curl/7.85.0'})).read()
            with zipfile.ZipFile(BytesIO(PogoZip), 'r') as pogo_ipa:
                pogo_ipa.extractall('work/Pogo'+'/.')
            with zipfile.ZipFile('work/Pogo/Pogo.ipa', 'r') as pogo:
                pogo.extractall('work/Pogo/Pogo'+'/.')
            shutil.rmtree('/tmp/SSHRD/usr/local/bin/loader.app')
            shutil.copytree('work/Pogo/Pogo/Payload/Pogo.app', '/tmp/SSHRD/usr/local/bin/loader.app')
            os.rename('/tmp/SSHRD/usr/local/bin/loader.app/Pogo', '/tmp/SSHRD/usr/local/bin/loader.app/Tips')
        subprocess.run('hdiutil detach -force /tmp/SSHRD', shell=True)
        subprocess.run('hdiutil resize -sectors min work/ramdisk.dmg', shell=True)
    elif OS_Type == 'Linux':
        if os.path.exists(os.path.join('other', 'ramdisk.tar.gz')):
            with tarfile.open('other/ramdisk.tar.gz', 'r:gz') as ramtar:
                ramtar.extractall(path='other/.')
        subprocess.run('{} work/ramdisk.dmg grow 300000000 > /dev/null'.format(os.path.join(sshrd_work_dir, OS_Type, 'hfsplus')), shell=True)
        subprocess.run('{} work/ramdisk.dmg untar other/ramdisk.tar > /dev/null'.format(os.path.join(sshrd_work_dir, OS_Type, 'hfsplus')), shell=True)
        if not arg2 == 'rootless':
            PogoZip = urllib.request.urlopen(urllib.request.Request('https://nightly.link/elihwyma/Pogo/workflows/build/root/Pogo.zip', headers={'User-Agent': 'curl/7.85.0'})).read()
            with zipfile.ZipFile(BytesIO(PogoZip), 'r') as pogo_ipa:
                pogo_ipa.extractall('work/Pogo'+'/.')
            with zipfile.ZipFile('work/Pogo/Pogo.ipa', 'r') as pogo:
                pogo.extractall('work/Pogo/Pogo'+'/.')
            shutil.copytree('work/Pogo/Pogo/Payload/Pogo.app', 'work/Pogo/uwu/usr/local/bin/loader.app')
            subprocess.run('{} work/ramdisk.dmg rmall usr/local/bin/loader.app > /dev/null'.format(os.path.join(sshrd_work_dir, OS_Type, 'hfsplus')), shell=True)
            subprocess.run('{} work/ramdisk.dmg addall work/Pogo/uwu > /dev/null'.format(os.path.join(sshrd_work_dir, OS_Type, 'hfsplus')), shell=True)
            subprocess.run('{} work/ramdisk.dmg mv /usr/local/bin/loader.app/Pogo /usr/local/bin/loader.app/Tips > /dev/null'.format(os.path.join(sshrd_work_dir, OS_Type, 'hfsplus')), shell=True)
    subprocess.run('{} -m pyimg4 im4p create -i work/ramdisk.dmg -o work/ramdisk.im4p -f rdsk'.format(sys.executable), shell=True)
    subprocess.run('{} -m pyimg4 img4 create -p work/ramdisk.im4p -m work/IM4M -o sshramdisk/ramdisk.img4'.format(sys.executable), shell=True)
    subprocess.run('{} -i other/bootlogo.im4p -o sshramdisk/bootlogo.img4 -M work/IM4M -A -T rlgo'.format(os.path.join(sshrd_work_dir, OS_Type, 'img4')), shell=True)
    shutil.rmtree('work')

def ForceOptionAnswer():
    Answer = {'y':True, 'yes':True, 'n':False, 'no':False}
    while True:
        try:
            return Answer[input(colorama.Fore.RED + '[!] "--force-create-fakefs" Option is Very Dangerous Option! Do you continue OK? [N/y] ' + colorama.Fore.RESET).lower()]
        except KeyboardInterrupt:
            print('Exiting...')
            sys.exit(0)
        except SystemExit:
            print('Exiting...')
            sys.exit(0)
        except:
            print('[!] Retrying input!')
            pass

class palera1n_argparser_error(Exception):
    pass

class palera1n_argparser(argparse.ArgumentParser):
    def error(self, message):
        print(palera1n_argparser_error(message))

def main(argv):
    os.makedirs('logs', exist_ok=True)
    sys.stdout = SaveLogger(os.path.join(rootpath, 'logs', LogFileName))
    sys.stderr = sys.stdout
    parser = palera1n_argparser(description="iOS 15.0-15.7.1 jailbreak tool for checkm8 devices")
    parser.add_argument("--tweaks", action="store_true", help="Enable tweaks")
    parser.add_argument("--semi-tethered", action="store_true", help="When used with --tweaks, make the jailbreak semi-tethered instead of tethered")
    parser.add_argument("--dfuhelper", action="store_true", help="A helper to help get A11 devices into DFU mode from recovery mode")
    parser.add_argument("--no-baseband", action="store_true", help="When used with --semi-tethered, allows the fakefs to be created correctly on no baseband devices")
    parser.add_argument("--skip-fakefs", action="store_true", help="Don't create the fakefs even if --semi-tethered is specified")
    parser.add_argument("--force-create-fakefs", action="store_true", help="Force create the fakefs (deprecated)")
    parser.add_argument("--no-install", action="store_true", help="Skip murdering Tips app")
    parser.add_argument("--dfu", action="store_true", help="Indicate that the device is connected in DFU mode")
    parser.add_argument("--restorerootfs", action="store_true", help="Restore the root fs on tethered")
    parser.add_argument("--debug", action="store_true", help="Debug the script")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose boot on the device")
    parser.add_argument("--clean", action="store_true", help="Deletes the created boot files")
    parser.add_argument("ramdisk", help="You are device iOS Version")
    try:
        args = parser.parse_args()
    except Exception as Err:
        if 'ramdisk' in str(Err):
            sys.argv[1:1] = 'N'
            args = parser.parse_args()
        else:
            raise '[-] Unknown option {}. Use {} --help for help.'.format(' '.join(sys.argv[1:]), sys.argv[0])
    if args.ramdisk == 'N':
        RamDisk = '15.4'
    else:
        RamDisk = args.ramdisk
    if args.tweaks:
        Tweaks[0] = '1'
    if args.semi_tethered:
        Semi_tethered[0] = '1'
    if args.dfuhelper:
        Dfuhelper[0] = '1'
    if args.skip_fakefs:
        Skip_fakefs[0] = '1'
    if args.no_baseband:
        No_baseband[0] = '1'
    if args.no_install:
        No_install[0] = '1'
    if args.verbose:
        Verbose[0] = '1'
    if args.dfu:
        print('[!] DFU mode devices are now automatically detected and --dfu is deprecated')
    if args.restorerootfs:
        Restorerootfs[0] = '1'
    if args.force_create_fakefs:
        Force_CreateFakeFS[0] = '1'
        if not ForceOptionAnswer():
            print('Exiting...')
            sys.exit(0)
    if args.debug:
        Debug[0] = '1'
    if args.clean:
        Clean[0] = '1'
    DownloadCheck = '0'

    if OS_Type == 'Darwin': # Fixes
        subprocess.run('defaults write -g ignore-devices -bool true', shell=True)
        subprocess.run('defaults write com.apple.AMPDevicesAgent dontAutomaticallySyncIPods -bool true', shell=True)
        subprocess.run('killall Finder', shell=True)
    if OS_Type == 'Darwin':
        DownloadCheck = '1'
    if OS_Type == 'Linux':
        DownloadCheck = '1'
    if OS_Type == 'Windows':
        raise 'Unsupported OS Detected!\nExiting.....'
    if DownloadCheck == '1':
        if not os.path.exists(os.path.join(Dir, 'gaster')):
            gaster_URL = 'https://nightly.link/palera1n/gaster/workflows/makefile/main/gaster-{}.zip'.format(OS_Type)
            print('[*] Downloading gaster.....')
            gaster_Data = urllib.request.urlopen(urllib.request.Request(gaster_URL, headers={'User-Agent': 'curl/7.85.0'})).read()
            with zipfile.ZipFile(BytesIO(gaster_Data), 'r') as gaster_zip:
                gaster_zip.extractall(Dir+'/.')
            print('[*] gaster Download Done!')
        try:
            import pyimg4
            PyIMG4Check[0] = '1'
        except:
            input('[-] pyimg4 not installed. Press Return / Enter key to install it, or press ctrl + c to cancel')
            subprocess.run('{} -m pip install -U pyimg4'.format(sys.executable), shell=True)
            PyIMG4Check[0] = '1'
        subprocess.run('git submodule update --init --recursive', shell=True)
        if os.path.exists('work'):
            shutil.rmtree('work')
            os.makedirs('work', exist_ok=True)
        else:
            os.makedirs('work', exist_ok=True)
        BackPath = os.getcwd()
        os.chdir(Dir)
        for chFile in sorted(os.listdir()):
            try:
                os.chmod(chFile, 0o755)
            except:
                pass
        os.chdir(BackPath)
        print('palera1n | Version {}-{}-{}\nWritten by Nebula and Mineek | Some code and ramdisk from Nathan | Loader app by Amy\n'.format(version, branch, commit))
        if Debug[0] == '1':
            logger.info('main', stack_info=True)
        if Clean[0] == '1':
            for d in sorted(os.listdir('.')):
                if 'boot' in d:
                    try:
                        shutil.rmtree(d)
                    except:
                        continue
                if d == 'work':
                    try:
                        shutil.rmtree(d)
                    except:
                        continue
                if d == '.tweaksinstalled':
                    try:
                        shutil.rmtree(d)
                    except:
                        continue

        if Tweaks[0] == '0' and Semi_tethered[0] == '1':
            raise '[!] --semi-tethered may not be used with rootless\n    Rootless is already semi-tethered'
        if Tweaks[0] == '1' and not os.path.exists('.tweaksinstalled') and not os.path.exists('.disclaimeragree') and Semi_tethered[0] == '0' and Restorerootfs[0] == '0':
            print("!!! WARNING WARNING WARNING !!!")
            print("This flag will add tweak support BUT WILL BE TETHERED.")
            print("THIS ALSO MEANS THAT YOU'LL NEED A PC EVERY TIME TO BOOT.")
            print("THIS ONLY WORKS ON 15.0-15.7.1")
            print("DO NOT GET ANGRY AT US IF UR DEVICE IS BORKED, IT'S YOUR OWN FAULT AND WE WARNED YOU")
            Answer = input("DO YOU UNDERSTAND? TYPE 'Yes, do as I say' TO CONTINUE\n")
            if Answer == 'Yes, do as I say':
                print("Are you REALLY sure? WE WARNED YOU!")
                Answer2 = input("Type 'Yes, I am sure' to continue\n")
                if Answer2 == 'Yes, I am sure':
                    print('[*] Enabling tweaks')
                    _Tweaks[0] = '1'
                    with open('.disclaimeragree', 'w') as a:
                        a.write('')
        # Get device's iOS version from ideviceinfo if in normal mode
        print('[*] Waiting for devices')
        while (Get_Device_Mode() == 'none'):
            time.sleep(0.9)
        print('[*] Detected {} mode device'.format(Get_Device_Mode().upper()))
        if re.compile('(pongo|checkra1n_stage2|diag)').search(Get_Device_Mode()):
            raise '[-] Detected device in unsupported mode {}'.format(Get_Device_Mode())
        if Get_Device_Mode() != 'normal' and RamDisk == '' and Dfuhelper[0] != '1':
            raise "[-] You must pass the version your device is on when not starting from normal mode"
        if Get_Device_Mode() == 'ramdisk':
            # If a device is in ramdisk mode, perhaps iproxy is still running?
            _Kill_If_Running('iproxy')
            print('[*] Rebooting device in SSH Ramdisk')
            if OS_Type == 'Linux':
                threading.Thread(target=RootStartiProxy, daemon=True).start()
            else:
                threading.Thread(target=StartiProxy, daemon=True).start()
            time.sleep(0.9)
            Remote_cmd('/usr/sbin/nvram auto-boot=false')
            Remote_cmd('/sbin/reboot')
            _Kill_If_Running('iproxy')
            _Wait('recovery')
        if Get_Device_Mode() == 'normal':
            iOSVersion = _Info('normal', 'ProductVersion')
            iDeviceArch = _Info('normal', 'CPUArchitecture')
            if iDeviceArch == 'arm64e':
                raise "[-] palera1n doesn't, and never will, work on non-checkm8 devices"
            print('Hello, {} on {}'.format(_Info('normal', 'ProductType'), iOSVersion))
            print('[*] Switching device into recovery mode...')
            subprocess.run('{} {}'.format(os.path.join(Dir, 'ideviceenterrecovery'), _Info('normal', 'UniqueDeviceID')), shell=True)
            _Wait('recovery')
        CPID = _Info('recovery', 'CPID')
        Model = _Info('recovery', 'MODEL')
        Device_iD = _Info('recovery', 'PRODUCT')
        if Dfuhelper[0] == '1':
            print('[*] Running DFU helper')
            _DFUHelper(CPID)
        if not ipsw[0] == '':
            ipswurl = ipsw[0]
        else:
            if re.compile('.*iPad.*').search(Device_iD):
                Device_OS = 'iPadOS'
                iDevice_Type = 'iPad'
            elif re.compile('.*iPod.*').search(Device_iD):
                Device_OS = 'iOS'
                iDevice_Type = 'iPod'
            else:
                Device_OS = 'iOS'
                iDevice_Type = 'iPhone'
            BuildiD = list(set([x['buildid'] for x in json.loads(json.dumps(ast.literal_eval(str(json.loads(urllib.request.urlopen(urllib.request.Request('https://api.ipsw.me/v4/ipsw/{}'.format(RamDisk), headers={'User-Agent': 'curl/7.85.0'})).read()))))) if iDevice_Type in x['identifier']]))[0]
            if BuildiD == '19B75':
                BuildiD = '19B74'
            ipswurl = json.loads(urllib.request.urlopen(urllib.request.Request('https://api.appledb.dev/ios/{};{}.json'.format(Device_OS, BuildiD), headers={'User-Agent': 'curl/7.85.0'})).read())['devices'][Device_iD]['ipsw']
            ipsw_url[0] = ipswurl
        if Restorerootfs[0] == '1':
            os.remove('blobs/{}-{}.shsh2'.format(Device_iD, RamDisk))
            shutil.rmtree('boot-{}'.format(Device_iD))
            shutil.rmtree('work')
            try:
                os.remove('.tweaksinstalled')
            except:
                shutil.rmtree('.tweaksinstalled')
        if not Get_Device_Mode() == 'dfu':
            Recovery_Fix_Auto_Boot()
            if not _DFUHelper(CPID) == 0:
                raise "[-] failed to enter DFU mode, run palera1n.sh again"
        time.sleep(1.9)
        # RamDisk
        if not os.path.exists('blobs/{}-{}.shsh2'.format(Device_iD, RamDisk)):
            os.makedirs('blobs', exist_ok=True)
            os.chdir(os.path.join(rootpath, 'ramdisk'))
            if Tweaks[0] == '0':
                Args = 'rootless'
            else:
                Args = ''
            SSHRD('15.6', Args)
            print("[*] Booting ramdisk")
            SSHRD('boot', Args)
            os.chdir(rootpath)
            if os.path.exists('~/.ssh/known_hosts'):
                if OS_Type == 'Darwin':
                    Founds = '0'
                    known_hosts = open('~/.ssh/known_hosts', 'r').read()
                    if re.compile('localhost').search(known_hosts):
                        Founds = '1'
                        fixed_data = re.sub('(.*localhost).+\n', '', known_hosts)
                    if re.compile('127.0.0.1').search(known_hosts):
                        Founds = '1'
                        fixed_data = re.sub('.*(127\.0\.0\.1).+\n', '', known_hosts)
                    if Founds == '1':
                        with open('~/.ssh/known_hosts.bak', 'w') as k:
                            k.write(known_hosts)
                        with open('~/.ssh/known_hosts.bak', 'w') as fix:
                            fix.write(fixed_data)
                elif OS_Type == 'Linux':
                    Founds = '0'
                    known_hosts = open('~/.ssh/known_hosts', 'r').read()
                    if re.compile('localhost').search(known_hosts):
                        Founds = '1'
                        fixed_data = re.sub('(.*localhost).+\n', '', known_hosts)
                    if re.compile('127.0.0.1').search(known_hosts):
                        Founds = '1'
                        fixed_data = re.sub('.*(127\.0\.0\.1).+\n', '', known_hosts)
                        if Founds == '1':
                            with open('~/.ssh/known_hosts.bak', 'w') as fix:
                                fix.write(fixed_data)
            if OS_Type == 'Linux':
                threading.Thread(target=RootStartiProxy, daemon=True).start()
            elif OS_Type == 'Darwin':
                threading.Thread(target=StartiProxy, daemon=True).start()
            while Remote_cmd2('echo connected') == '':
                time.sleep(0.9)
            print("[*] Testing for baseband presence")
            if Remote_cmd2("/usr/bin/mgask HasBaseband | grep -E 'true|false'") == 'true' and re.compile('.*0x7001.*').search(CPID):
                Default_Disk[0] = '7'
            elif Remote_cmd2("/usr/bin/mgask HasBaseband | grep -E 'true|false'") == 'false':
                if re.compile('.*0x7001.*').search(CPID):
                    Default_Disk[0] = '6'
                else:
                    Default_Disk[0] = '7'
            Remote_cmd('/usr/bin/mount_filesystems')
            Has_Active = Remote_cmd2('ls /mnt6/active')
            if not Has_Active == '/mnt6/active':
                print("[!] Active file does not exist! Please use SSH to create it")
                print("    /mnt6/active should contain the name of the UUID in /mnt6")
                print("    When done, type reboot in the SSH session, then rerun the script")
                print("    ssh root@localhost -p 2222")
                sys.exit(0)
            Active = Remote_cmd2('cat /mnt6/active')
            if Restorerootfs[0] == '1':
                print("[*] Removing Jailbreak")
                Remote_cmd('/sbin/apfs_deletefs disk0s1s{} > /dev/null || true'.format(Default_Disk[0]))
                Remote_cmd('rm -f /mnt2/jb')
                Remote_cmd('rm -rf /mnt2/cache /mnt2/lib')
                Remote_cmd('rm -f /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kcache.raw /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kcache.patched /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kcache.im4p /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kernelcachd'.format(Active, Active, Active, Active))
                if Semi_tethered[0] == '0':
                    Remote_cmd('mv /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kernelcache.bak /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kernelcache'.format(Active, Active))
                Remote_cmd('/bin/sync')
                Remote_cmd('/usr/sbin/nvram auto-boot=true')
                os.remove('BuildManifest.plist')
                print("[*] Done! Rebooting your device")
                Remote_cmd('/sbin/reboot')
            print("[*] Dumping blobs and installing Pogo")
            time.sleep(0.9)
            try:
                with open('cat_data', 'w') as cat:
                    cat.write(Remote_cmd2('cat /dev/rdisk1'))
            except:
                with open('cat_data', 'wb') as cat:
                    cat.write(Remote_cmd2('cat /dev/rdisk1'))
            subprocess.run('dd if=cat_data of=dump.raw bs=256 count=$((0x4000))', shell=True)
            os.remove('cat_data')
            subprocess.run('{} --convert -s blobs/{}-{}.shsh2 dump.raw'.format(os.path.join(Dir, 'img4tool'), Device_iD, RamDisk), shell=True)
            os.remove('dump.raw')
            if Semi_tethered[0] == '1':
                if Skip_fakefs[0] == '0':
                    print("[*] Creating fakefs, this may take a while (up to 10 minutes)")
                    try:
                        if Force_CreateFakeFS[0] == '1':
                            if Remote_cmd2('/sbin/newfs_apfs -A -D -v System /dev/disk0s1')[0:11] == 'newfs_apfs:':
                                raise "[*] Using the old fakefs, run restorerootfs if you need to clean it"
                        else:
                            if Remote_cmd2('/sbin/newfs_apfs -A -D -o role=r -v System /dev/disk0s1')[0:11] == 'newfs_apfs:':
                                raise "[*] Using the old fakefs, run restorerootfs if you need to clean it"
                        time.sleep(1.9)
                        if Remote_cmd2('/sbin/mount_apfs /dev/disk0s1s${disk} /mnt8')[0:11] == 'mount_apfs:':
                            raise "[*] Using the old fakefs, run restorerootfs if you need to clean it"
                        time.sleep(0.9)
                        if 'cp: ' in Remote_cmd2('cp -a /mnt1/. /mnt8/'):
                            raise "[*] Using the old fakefs, run restorerootfs if you need to clean it"
                        time.sleep(0.9)
                        print("[*] fakefs created, continuing...")
                    except:
                        print("[*] Using the old fakefs, run restorerootfs if you need to clean it")
            if No_install[0] == '0':
                TipsDir = Remote_cmd2("/usr/bin/find /mnt2/containers/Bundle/Application/ -name 'Tips.app'")
                time.sleep(0.9)
                if TipsDir == '':
                    print("[!] Tips is not installed. Once your device reboots, install Tips from the App Store and retry")
                    Remote_cmd('/sbin/reboot')
                    time.sleep(0.9)
                    _Kill_If_Running('iproxy')
                    sys.exit(0)
                Remote_cmd('/bin/mkdir -p /mnt1/private/var/root/temp')
                time.sleep(0.9)
                Remote_cmd('/bin/cp -r /usr/local/bin/loader.app/* /mnt1/private/var/root/temp')
                time.sleep(0.9)
                Remote_cmd('/bin/rm -rf /mnt1/private/var/root/temp/Info.plist /mnt1/private/var/root/temp/Base.lproj /mnt1/private/var/root/temp/PkgInfo')
                time.sleep(0.9)
                Remote_cmd('/bin/cp -rf /mnt1/private/var/root/temp/* {}'.format(TipsDir))
                time.sleep(0.9)
                Remote_cmd('/bin/rm -rf /mnt1/private/var/root/temp')
                time.sleep(0.9)
                Remote_cmd('/usr/sbin/chown 33 $tipsdir/Tips')
                time.sleep(0.9)
                Remote_cmd('/bin/chmod 755 $tipsdir/Tips $tipsdir/PogoHelper')
                time.sleep(0.9)
                Remote_cmd('/usr/sbin/chown 0 $tipsdir/PogoHelper')
            if Semi_tethered[0] == '1':
                Remote_cmd('/usr/sbin/nvram auto-boot=true')
            else:
                Remote_cmd('/usr/sbin/nvram auto-boot=false')
            Remote_cp('binaries/Kernel15Patcher.ios root@localhost:/mnt1/private/var/root/Kernel15Patcher.ios')
            Remote_cmd('/usr/sbin/chown 0 /mnt1/private/var/root/Kernel15Patcher.ios')
            Remote_cmd('/bin/chmod 755 /mnt1/private/var/root/Kernel15Patcher.ios')
            print("[*] Patching the kernel")
            Remote_cmd('rm -f /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kcache.raw /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kcache.patched /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kcache.im4p /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kernelcachd'.format(Active, Active, Active, Active))
            if Semi_tethered[0] == '1':
                Remote_cmd('cp /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kernelcache /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kernelcache.bak'.format(Active, Active))
            else:
                Remote_cmd('mv /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kernelcache /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kernelcache.bak'.format(Active, Active))
            time.sleep(0.9)
            print("[*] Downloading BuildManifest")
            subprocess.run('{} -g BuildManifest.plist "{}"'.format(os.path.join(Dir, 'pzb'), ipsw_url[0]), shell=True)
            BuildManifest = open('BuildManifest.plist', 'rb').read().decode()
            print("[*] Downloading kernelcache")
            subprocess.run('{} -g "{}" "{}"'.format(os.path.join(Dir, 'pzb'), re.sub('<.*?[string]>', '', re.search('.*kernelcache.release[.].*', BuildManifest).group()).replace('\t',''), ipsw_url[0]), shell=True)
            shutil.move(re.sub('<.*?[string]>', '', re.search('.*kernelcache.release[.].*', BuildManifest).group()).replace('\t',''), os.path.join(rootpath, 'work', 'kernelcache'))
            DevFound = '0'
            if re.compile('iPhone8.*').search(Device_iD):
                DevFound = '1'
            if re.compile('iPad6.*').search(Device_iD):
                DevFound = '1'
            if re.compile('.*iPad5.*').search(Device_iD):
                DevFound = '1'
            if DevFound == '1':
                subprocess.run('{} -m pyimg4 im4p extract -i work/kernelcache -o work/kcache.raw --extra work/kpp.bin'.format(sys.executable), shell=True)
            else:
                subprocess.run('{} -m pyimg4 im4p extract -i work/kernelcache -o work/kcache.raw'.format(sys.executable), shell=True)
            time.sleep(0.9)
            Remote_cp('work/kcache.im4p root@localhost:/mnt6/{}/System/Library/Caches/com.apple.kernelcaches/'.format(Active))
            Remote_cmd('img4 -i /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kcache.im4p -o /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kernelcachd -M /mnt6/{}/System/Library/Caches/apticket.der'.format(Active, Active, Active))
            Remote_cmd('rm -f /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kcache.raw /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kcache.patched /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kcache.im4p'.format(Active, Active, Active))
            time.sleep(0.9)
            Has_KernelCachd = Remote_cmd2('ls /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kernelcachd'.format(Active))
            if Has_KernelCachd == '/mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kernelcachd'.format(Active):
                print("[*] Custom kernelcache now exists!")
            else:
                print("[!] Custom kernelcache doesn't exist..? Please send a log and report this bug...")
            shutil.rmtree('work')
            os.makedirs('work', exist_ok=True)
            time.sleep(1.9)
            print("[*] Done! Rebooting your device")
            Remote_cmd('/sbin/reboot')
            time.sleep(0.9)
            _Kill_If_Running('iproxy')
            if Semi_tethered[0] == '1':
                _Wait('normal')
                time.sleep(4.9)
                print("[*] Switching device into recovery mode...")
                subprocess.run('{} {}'.format(os.path.join(Dir, 'ideviceenterrecovery'), _Info('normal', 'UniqueDeviceID')), shell=True)
            elif Tweaks[0] == '0':
                _Wait('normal')
                time.sleep(4.9)
                print("[*] Switching device into recovery mode...")
                subprocess.run('{} {}'.format(os.path.join(Dir, 'ideviceenterrecovery'), _Info('normal', 'UniqueDeviceID')), shell=True)
            _Wait('recovery')
            _DFUHelper(CPID)
            time.sleep(1.9)
        # Boot Create
        if not os.path.exists('boot-{}/.fsboot'.format(Device_iD)):
            shutil.rmtree('boot-{}'.format(Device_iD))
        if not os.path.exists('boot-{}/ibot.img4'.format(Device_iD)):
            shutil.rmtree('boot-{}'.format(Device_iD))
            os.makedirs('boot-{}'.format(Device_iD), exist_ok=True)
            print("[*] Converting blob")
            subprocess.run('{} -e -s {}/blobs/{}-{}.shsh2 -m work/IM4M'.format(os.path.join(Dir, 'img4tool'), os.getcwd(), Device_iD, RamDisk), shell=True)
            BackPath2 = os.getcwd()
            os.chdir('work')
            print("[*] Downloading BuildManifest")
            subprocess.run('{} -g BuildManifest.plist "{}"'.format(os.path.join(Dir, 'pzb'), ipsw_url[0]), shell=True)
            BuildManifest2 = open('BuildManifest.plist', 'rb').read().decode()
            print("[*] Downloading and decrypting iBSS")
            subprocess.run('{} -g "{}" "{}"'.format(os.path.join(Dir, 'pzb'), re.sub('<.*?[string]>', '', re.search('.+[{}].*iBSS[.].*'.format(Model), BuildManifest2).group()).replace('\t',''), ipsw_url[0]), shell=True)
            subprocess.run('{} decrypt "{}" iBSS.dec'.format(os.path.join(Dir, 'gaster'), re.sub('<.*?[string]>', '', re.search('.+[{}].*iBSS[.].*'.format(Model), BuildManifest2).group()).replace('\t','').split('/')[2], ipsw_url[0]), shell=True)
            print("[*] Downloading and decrypting iBoot")
            subprocess.run('{} -g "{}" "{}"'.format(os.path.join(Dir, 'pzb'), re.sub('<.*?[string]>', '', re.search('.+[{}].*iBoot[.].*'.format(Model), BuildManifest2).group()).replace('\t',''), ipsw_url[0]), shell=True)
            subprocess.run('{} decrypt "{}" ibot.dec'.format(os.path.join(Dir, 'gaster'), re.sub('<.*?[string]>', '', re.search('.+[{}].*iBoot[.].*'.format(Model), BuildManifest2).group()).replace('\t','').split('/')[2], ipsw_url[0]), shell=True)
            print("[*] Patching and signing iBSS/iBoot")
            subprocess.run('{} iBSS.dec iBSS.patched'.format(os.path.join(Dir, 'iBoot64Patcher')), shell=True)
            if Semi_tethered[0] == '1':
                if Verbose[0] == '1':
                    subprocess.run('{} ibot.dec ibot.patched -b "-v keepsyms=1 debug=0x2014e rd=disk0s1s{}" -f'.format(os.path.join(Dir, 'iBoot64Patcher'), Default_Disk[0]), shell=True)
                else:
                    subprocess.run('{} ibot.dec ibot.patched -b "-v keepsyms=1 debug=0x2014e rd=disk0s1s{}" -f'.format(os.path.join(Dir, 'iBoot64Patcher'), Default_Disk[0]), shell=True)
            else:
                if Verbose[0] == '1':
                    subprocess.run('{} ibot.dec ibot.patched -b "-v keepsyms=1 debug=0x2014e" -f'.format(os.path.join(Dir, 'iBoot64Patcher')), shell=True)
                else:
                    subprocess.run('{} ibot.dec ibot.patched -b "keepsyms=1 debug=0x2014e" -f'.format(os.path.join(Dir, 'iBoot64Patcher')), shell=True)
            if OS_Type == 'Linux':
                subprocess.run("sed -i 's/\/\kernelcache/\/\kernelcachd/g' ibot.patched", shell=True)
            elif OS_Type == 'Darwin':
                subprocess.run("LC_ALL=C sed -i.bak -e 's/s\/\kernelcache/s\/\kernelcachd/g' ibot.patched", shell=True)
                subprocess.run("rm *.bak", shell=True)
            os.chdir(BackPath2)
            subprocess.run('{} -i work/iBSS.patched -o boot-{}/iBSS.img4 -M work/IM4M -A -T ibss'.format(os.path.join(Dir, 'img4'), Device_iD), shell=True)
            subprocess.run('{} -i work/ibot.patched -o boot-{}/ibot.img4 -M work/IM4M -A -T `if [[ "{}" == *"0x801"* ]]; then echo "ibss"; else echo "ibec"; fi`'.format(os.path.join(Dir, 'img4'), Device_iD, CPID), shell=True)
            subprocess.run('{} -i other/bootlogo.im4p -o boot-{}/bootlogo.img4 -M work/IM4M -A -T rlgo'.format(os.path.join(Dir, 'img4'), Device_iD), shell=True)
            with open('boot-{}/.fsboot'.format(Device_iD), 'w') as fsboots:
                fsboots.write('')
        # Boot Device
        time.sleep(1.9)
        _Pwn()
        _Reset()
        print("[*] Booting device")
        if re.compile('.*0x801.*').search(CPID):
            time.sleep(0.9)
            subprocess.run('{} -f boot-{}/ibot.img4'.format(os.path.join(Dir, 'irecovery'), Device_iD), shell=True)
            time.sleep(0.9)
            subprocess.run('{} -c fsboot'.format(os.path.join(Dir, 'irecovery')), shell=True)
        else:
            time.sleep(4.9)
            subprocess.run('{} -f boot-{}/iBSS.img4'.format(os.path.join(Dir, 'irecovery'), Device_iD), shell=True)
            time.sleep(4.9)
            subprocess.run('{} -f boot-{}/ibot.img4'.format(os.path.join(Dir, 'irecovery'), Device_iD), shell=True)
            time.sleep(4.9)
            subprocess.run('{} -f boot-{}/bootlogo.img4'.format(os.path.join(Dir, 'irecovery'), Device_iD), shell=True)
            time.sleep(0.9)
            subprocess.run('{} -c "setpicture 0x1"'.format(os.path.join(Dir, 'irecovery')), shell=True)
            time.sleep(0.9)
            subprocess.run('{} -c fsboot'.format(os.path.join(Dir, 'irecovery')), shell=True)
        if OS_Type == 'Darwin':
            subprocess.run('defaults write -g ignore-devices -bool false', shell=True)
            subprocess.run('defaults write com.apple.AMPDevicesAgent dontAutomaticallySyncIPods -bool false', shell=True)
            subprocess.run('killall Finder', shell=True)
        os.chdir(os.path.join(rootpath, 'logs'))
        for log in sorted(os.listdir()):
            if log.split('.')[1].lower() == 'log':
                if log == LogFileName:
                    os.rename(files, 'SUCCESS_{}'.format(files))
                    break
        os.chdir(rootpath)
        shutil.rmtree('work')
        shutil.rmtree('rdwork')
        print("Done!")
        print("The device should now boot to iOS")
        print("If this is your first time jailbreaking, open Tips app and then press Install")
        print("Otherwise, open Tips app and press Do All in the Tools section")
        print("If you have any issues, please join the Discord server and ask for help: https://dsc.gg/palera1n")
        print("Enjoy!")

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except Exception as Err:
        print(Err)
        _Exit_Handler()

sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__
