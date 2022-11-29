#!/usr/bin/env python3

'''
Name: palera1n python3 edition
Python Script Author: CrossDarkrix
Version: 1.3.5(python3)
'''


import argparse, ast, json, os, platform, re, shutil, subprocess, sys, tarfile, threading, time, urllib.request, zipfile
from datetime import datetime
from math import floor
from io import BytesIO

try:
    from pyimg4.__main__ import cli as pyimg4
except:
    input('[-] pyimg4 not installed. Press Return / Enter key to install it, or press ctrl + c to cancel')
    subprocess.run('{} -m pip install -U pyimg4'.format(sys.executable), shell=True)
    from pyimg4.__main__ import cli as pyimg4
    
try:
    import colorama
except:
    print('Colorama not Installed!Auto installing...')
    subprocess.run('{} -m pip install -U colorama'.format(sys.executable), shell=True)
    import colorama

colorama.init()

class logger(object): # output stdout & logfile.
    def __init__(self, filename):
        self.console = sys.__stdout__
        self.log_file = open(filename, 'w', encoding='utf-8')

    def write(self, m):
        self.console.write(m)
        self.log_file.write(m)

    def flush(self):
        self.console.flush()
        self.log_file.flush()

class palera1n_argparser_error(Exception):
    pass

class palera1n_argparser(argparse.ArgumentParser):
    def error(self, message):
        print(palera1n_argparser_error(message))

class palera1n(object):
    def __init__(self):
        self.ipsw_url = ''
        self.version = '1.3.5_py'
        self.os_type = platform.system()
        self.default_path = os.getcwd()
        os.makedirs(os.path.join(self.default_path, 'logs'), exist_ok=True)
        self.binary_path = os.path.join(self.default_path, 'binaries', self.os_type)
        self.git_commit = subprocess.Popen('git rev-parse --short HEAD', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode()
        self.git_branch = subprocess.Popen('git rev-parse --abbrev-ref HEAD', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode()
        if self.git_commit == '':
            self.git_commit = 'None'
        if self.git_branch == '':
            self.git_branch = 'None'
        self.default_logfilename = '{}-{}-{}.log'.format(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'), platform.system(), platform.release())
        self.tweak_option = '0'
        self.semi_tethered_option = '0'
        self.DFUHelper_option = '0'
        self.skip_fakefs_option = '0'
        self.no_baseband_option = '0'
        self.no_install_option = '0'
        self.verbose_option = '0'
        self.restorerootfs_option = '0'
        self.force_createfs_option = '0'
        self.clean_option = '0'
        self.pyimg4_check = '0'
        self.default_disk_numbar = 8
        self.default_device_id = ''
        self.detected_device_mode = ''
        sys.stdout = logger(os.path.join(self.default_path, 'logs', self.default_logfilename))
        sys.stderr = sys.stdout
        self.argparser = palera1n_argparser(description="iOS 15.0-15.7.1 jailbreak tool for checkm8 devices")
        self.argparser.add_argument("--tweaks", action="store_true", help="Enable tweaks")
        self.argparser.add_argument("--semi-tethered", action="store_true", help="When used with --tweaks, make the jailbreak semi-tethered instead of tethered")
        self.argparser.add_argument("--dfuhelper", action="store_true", help="A helper to help get A11 devices into DFU mode from recovery mode")
        self.argparser.add_argument("--no-baseband", action="store_true", help="When used with --semi-tethered, allows the fakefs to be created correctly on no baseband devices")
        self.argparser.add_argument("--skip-fakefs", action="store_true", help="Don't create the fakefs even if --semi-tethered is specified")
        self.argparser.add_argument("--force-create-fakefs", action="store_true", help="Force create the fakefs (deprecated)")
        self.argparser.add_argument("--no-install", action="store_true", help="Skip murdering Tips app")
        self.argparser.add_argument("--restorerootfs", action="store_true", help="Restore the root fs on tethered")
        self.argparser.add_argument("--verbose", action="store_true", help="Enable verbose boot on the device")
        self.argparser.add_argument("--clean", action="store_true", help="Deletes the created boot files")
        self.argparser.add_argument("ramdisk", help="You are device iOS Version")
        try:
            self.args = self.argparser.parse_args()
        except Exception as Error:
            if 'ramdisk' in str(Error):
                sys.argv[1:1] = 'N'
                self.args = parser.parse_args()
            else:
                print('[-] Unknown option {}. Use {} --help for help.'.format(' '.join(sys.argv[1:]), sys.argv[0]))
                sys.exit(1)
        if self.args.ramdisk == 'N':
            self.ramdisk = '15.4'
        else:
            self.ramdisk = self.args.ramdisk
        if self.args.tweaks:
            self.tweak_option = '1'
        if self.args.semi_tethered:
            self.semi_tethered_option = '1'
        if self.args.dfuhelper:
            self.DFUHelper_option = '1'
        if self.args.skip_fakefs:
            self.skip_fakefs_option = '1'
        if self.args.no_baseband:
            self.no_baseband_option = '1'
        if self.args.no_install:
            self.no_install_option = '1'
        if self.args.verbose:
            self.verbose_option = '1'
        if self.args.force_create_fakefs:
            if not self.option_confirm():
                sys.exit(0)
            else:
                self.force_createfs_option = '1'
        if self.args.restorerootfs:
            self.restorerootfs_option = '1'
        if self.args.clean:
            self.clean_option = '1'
        try:
            self.main()
        except Exception as Err:
            print('[!] {}'.format(Err))
            self.exit_handler()

    def remote_command_sender(self, cmd):
        out, err = subprocess.Popen('{} -p "alpine" ssh -o StrictHostKeyChecking=no -p2222 root@localhost "{}"'.format(os.path.join(Dir, 'sshpass'), cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        output = out.decode()
        errors = err.decode()
        if not output == '':
            return output
        elif not errors == '':
            return errors

    def remote_cp(self, cmd):
        subprocess.run('{} -p "alpine" scp -o StrictHostKeyChecking=no -P2222 {}'.format(os.path.join(Dir, 'sshpass'), cmd), shell=True)
        return

    def step(self, numbar, message):
        try:
            num = int(numbar)
        except:
            num = floor(numbar)
        for s in reversed(range(num)):
            try:
                print(colorama.Fore.CYAN + '({}) {}'.format(message, s), end='\r', flush=True)
            except:
                pass
            time.sleep(1)
        print('{} (0)\n'.format(message), end='\r', flush=True)
        return

    def recovery_fix_auto_boot(self):
        if self.tweak_option == '1':
            subprocess.run('{} -c "setenv auto-boot false"'.format(os.path.join(self.binary_path, 'irecovery')), shell=True)
            subprocess.run('{} -c "saveenv"'.format(os.path.join(self.binary_path, 'irecovery')), shell=True)
        else:
            subprocess.run('{} -c "setenv auto-boot true"'.format(os.path.join(self.binary_path, 'irecovery')), shell=True)
            subprocess.run('{} -c "saveenv"'.format(os.path.join(self.binary_path, 'irecovery')), shell=True)
        if self.semi_tethered_option == '1':
            subprocess.run('{} -c "setenv auto-boot true"'.format(os.path.join(self.binary_path, 'irecovery')), shell=True)
            subprocess.run('{} -c "saveenv"'.format(os.path.join(self.binary_path, 'irecovery')), shell=True)
        return

    def info(self, arg, keywords):
        if arg == 'recovery':
            try:
                device_info = re.search('({}:) (.+)'.format(keywords), subprocess.Popen('{} -q'.format(os.path.join(self.binary_path, 'irecovery')), shell=True, stdout=subprocess.PIPE).communicate()[0].decode()).group(2)
            except:
                device_info = ''
        elif arg == 'normal':
            try:
                device_info = re.search('({}:) (.+)'.format(keywords), subprocess.Popen('{}'.format(os.path.join(self.binary_path, 'ideviceinfo')), shell=True, stdout=subprocess.PIPE).communicate()[0].decode()).group(2)
            except:
                device_info = ''
        return device_info

    def pwn(self):
        pwnd = info('recovery', 'PWND')
        if pwnd == '':
            print('[*] Pwning device')
            subprocess.run('{} pwn'.format(os.path.join(self.binary_path, 'gaster')), shell=True)
            time.sleep(2)
        return

    def reset(self):
        print('[*] Resetting DFU state')
        subprocess.run('{} reset'.format(os.path.join(self.binary_path, 'gaster')), shell=True)
        return

    def get_device_mode(self):
        if self.os_type == 'Darwin':
            _aple = ['']
            while _aple[0] == '':
                try:
                    _aple = re.findall('(?<= ID: ).+', subprocess.Popen('system_profiler SPUSBDataType', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode())
                    break
                except:
                    _aple = ['']
                    time.sleep(0.5)
            apples = []
            for i, x in enumerate(_aple):
                try:
                    if '0x05ac' in x:
                        apples.append(_aple[i-1].split('x')[1])
                except:
                    apples.append('')
        elif self.os_type == 'Linux':
            __aple = ['']
            while __aple[0] == '':
                try:
                    __aple = subprocess.Popen('lsusb', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode().split('\n')
                    break
                except:
                    __aple = ['']
                    time.sleep(0.5)
            _aple = []
            for x in __aple:
                try:
                    if '05ac:' in x:
                        _aple.append(x)
                except:
                    _aple.append('none')
            apples = []
            for xx in _aple:
                try:
                    apples.append(xx.split(' ')[5].split(':')[1])
                except:
                    apples.append('none')
        count = 0
        for devices in apples:
            if devices == '12ab':
                self.detected_device_mode = 'normal'
                count += 1
            if devices == '12a8':
                self.detected_device_mode = 'normal'
                count += 1
            if devices == '1281':
                self.detected_device_mode = 'recovery'
                count += 1
            if devices  == '1227':
                self.detected_device_mode = 'dfu'
                count += 1
            if devices  == '1222':
                self.detected_device_mode = 'diag'
                count += 1
            if devices == '1338':
                self.detected_device_mode = 'checkra1n_stage2'
                count += 1
            if devices == '4141':
                self.detected_device_mode = 'pongo'
                count += 1
        if count == 0:
            self.detected_device_mode  = 'none'
        if 2 <= count:
            print('[-] Please attach only one device')
            sys.exit(1)
        if self.os_type == 'Linux':
            _ramdisk = ''
            while _ramdisk == '':
                try:
                    _ramdisk = subprocess.Popen('cat /sys/bus/usb/devices/*/serial', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode()
                    break
                except:
                    _ramdisk = ''
                    time.sleep(0.5)
            try:
                if 'ramdisk tool' in re.search('ramdisk tool (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) [0-9]{1,2} [0-9]{1,4} [0-9]{2}:[0-9]{2}:[0-9]{2}', re.search('.*(\n{1})', _ramdisk).group().split('\n')[0]).group():
                    self.detected_device_mode = 'ramdisk'
            except:
                pass
        if self.os_type == 'Darwin':
            _ramdisk = ''
            while _ramdisk == '':
                try:
                    _ramdisk = subprocess.Popen('system_profiler SPUSBDataType', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode()
                    break
                except:
                    _ramdisk = ''
                    time.sleep(0.5)
            try:
                if 'ramdisk tool' in re.search('ramdisk tool (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) [0-9]{1,2} [0-9]{1,4} [0-9]{2}:[0-9]{2}:[0-9]{2}', re.search('(Serial Number).*', _ramdisk).group().split(': ')[1]).group():
                    self.detected_device_mode = 'ramdisk'
            except:
                pass
        return self.detected_device_mode

    def wait(self, arg):
        if not self.get_device_mode() == arg:
            print('[*] Waiting for device in {} mode'.format(arg))
            while True:
                if not self.get_device_mode() == arg:
                    time.sleep(1)
                else:
                    break
        if arg == 'recovery':
            self.recovery_fix_auto_boot()
        return

    def _dfu_step_back4(self):
        self.step(4, self.stepone)
        return

    def dfuhelper(self, arg):
        dev_id = self.info('normal', 'ProductType')
        if re.compile('0x801.*').search(arg) and not re.compile('.*iPad.*').search(self.info('normal', 'ProductType')):
            self.stepone = 'Hold volume down + side button'
        else:
            self.stepone = 'Hold home + power button'
        input('[*] Press Return / Enter key when ready for DFU mode')
        self.step(3, 'Get Ready')
        threading.Thread(target=self._dfu_step_back4, daemon=True).start()
        time.sleep(3)
        subprocess.run('{} -c "reset"'.format(os.path.join(self.binary_path, 'irecovery')), shell=True)
        self.step(1, 'Keep holding')
        if re.compile('0x801.*').search(arg) and not re.compile('.*iPad.*').search(self.info('normal', 'ProductType')):
            self.step(10, 'Release side button, but keep holding volume down')
        else:
            self.step(10, 'Release power button, but keep holding home button')
        time.sleep(1)
        if self.get_device_mode() == 'dfu':
            print('[*] Device entered DFU!')
            return 0
        else:
            print('[-] Device did not enter DFU mode, rerun the script and try again')
            return 1

    def kill_if_running(self, pname):
        _process = 'none'
        while _process == 'none':
            try:
                _process = subprocess.Popen('pgrep -u root -xf "{}"'.format(pname), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPEs).communicate()[0].decode()
                if not _process == '':
                    subprocess.run('sudo killall {}'.format(pname), shell=True)
                    break
                else:
                    _process2 = 'none'
                    time.sleep(0.5)
                    while _process2 == 'none':
                        try:
                            _process2 = subprocess.Popen('pgrep -x "{}"'.format(pname), shell=True, stdout=subprocess.PIPE).communicate()[0].decode()
                            if not _process2 == '':
                                subprocess.run('killall {}'.format(pname), shell=True)
                                break
                        except:
                            _process2 = 'none'
                            time.sleep(0.5)
                    break
            except:
                _process = 'none'
                time.sleep(0.5)

    def exit_handler(self):
        if self.os_type == 'Darwin':
            subprocess.run('defaults write -g ignore-devices -bool false', shell=True)
            subprocess.run('defaults write com.apple.AMPDevicesAgent dontAutomaticallySyncIPods -bool false', shell=True)
            subprocess.run('killall Finder', shell=True)
        os.chdir(os.path.join(self.default_path, 'logs'))
        for logs in sorted(os.listdir()):
            if logs.split('.')[1].lower() == 'log' and logs == self.default_logfilename:
                os.rename(logs, 'FAIL_{}'.format(logs))
                break
            else:
                continue
        print("[*] A failure log has been made. If you're going to make a GitHub issue, please attach the latest log.")
        sys.exit(1)

    def starting_iproxy(self):
        subprocess.run('{} -2222 22'.format(os.path.join(self.binary_path, 'iproxy')), shell=True)
        return

    def starting_root_iproxy(self):
        subprocess.run('sudo {} -2222 22'.format(os.path.join(self.binary_path, 'iproxy')), shell=True)
        return

    def kerneldiff(self, original, patched, arg):
        sizeP = os.path.getsize(patched)
        sizeO = os.path.getsize(original)
        if not sizeP == sizeO:
            print("size does not match, can't compare files! exiting...")
            sys.exit(1)
        patched_data = open(patched, 'rb').read()
        original_data = open(original, 'rb').read()
        a = 0
        diff = []
        with open(arg, 'w+') as diff_file:
            diff_file.write('#AMFI\n\n')
            for d in range(sizeO):
                original_byte = original_data[d]
                patched_byte = patched_data[d]
                if not original_byte == patched_byte:
                    if a == 1e6:
                        for dif in diff:
                            diff_file.write('{} {} {}\n'.format(dif[0], dif[1], dif[2]))
                        diff = []
                        a = 0
                    diff.append([hex(d), hex(original_byte), hex(patched_byte)])
                    a += 1
            for dif2 in diff:
                diff_file.write('{} [] {}\n'.format(dif2[0], dif[1], dif[2]))
        return

    def sshrd_sh(self, arg, arg2='', arg3=''):
        if arg == '':
            print("1st argument: iOS version for the ramdisk\n")
            sys.exit(1)
        if arg == 'boot':
            if not os.path.exists(os.path.join(self.default_path, 'sshramdisk', 'iBSS.img4')):
                print("[-] Please create an SSH ramdisk first!")
                sys.exit(1)
            subprocess.run('{} pwn'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'gaster')), shell=True)
            time.sleep(0.5)
            subprocess.run('{} reset'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'gaster')), shell=True)
            time.sleep(0.5)
            subprocess.run('{} -f {}'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'irecovery'), os.path.join('sshramdisk', 'iBSS.img4')), shell=True)
            time.sleep(3)
            subprocess.run('{} -f {}'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'irecovery'), os.path.join('sshramdisk', 'iBEC.img4')), shell=True)
            if self.sshrd_check == '0x8010':
                self.sshrd_device_check = '1'
                pass
            if self.sshrd_check == '0x8015':
                self.sshrd_device_check = '1'
                pass
            if self.sshrd_check == '0x8010':
                self.sshrd_device_check = '1'
                pass
            if self.sshrd_check == '0x8011':
                self.sshrd_device_check = '1'
                pass
            if self.sshrd_check == '0x8012':
                self.sshrd_device_check = '1'
                pass
            if self.sshrd_device_check == '1':
                subprocess.run('{} -c go'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'irecovery')), shell=True)
                time.sleep(7)
            else:
                time.sleep(7)
            subprocess.run('{} -f {}'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'irecovery'), os.path.join('sshramdisk', 'bootlogo.img4')), shell=True)
            time.sleep(1)
            subprocess.run('{} -c "setpicture 0x1"'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'irecovery')), shell=True)
            time.sleep(1)
            subprocess.run('{} -f {}'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'irecovery'), os.path.join('sshramdisk', 'ramdisk.img4')), shell=True)
            time.sleep(1)
            subprocess.run('{} -c ramdisk'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'irecovery')), shell=True)
            time.sleep(1)
            subprocess.run('{} -f {}'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'irecovery'), os.path.join('sshramdisk', 'devicetree.img4')), shell=True)
            time.sleep(1)
            subprocess.run('{} -c devicetree'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'irecovery')), shell=True)
            time.sleep(1)
            subprocess.run('{} -f {}'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'irecovery'), os.path.join('sshramdisk', 'trustcache.img4')), shell=True)
            time.sleep(1)
            subprocess.run('{} -c firmware'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'irecovery')), shell=True)
            time.sleep(1)
            subprocess.run('{} -f {}'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'irecovery'), os.path.join('sshramdisk', 'kernelcache.img4')), shell=True)
            time.sleep(1)
            subprocess.run('{} -c bootx'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'irecovery')), shell=True)
            return
        if not arg == '' and not arg == 'boot':
            self.sshrd_gaster_download_check = '0'
            if self.os_type == 'Darwin':
                self.sshrd_gaster_download_check = '1'
            if self.os_type == 'Linux':
                self.sshrd_gaster_download_check = '1'
            if self.os_type == 'Windows':
                print('Unsupported OS Detected!\nExiting.....')
                sys.exit(1)
            if self.sshrd_gaster_download_check == '1':
                if not os.path.exists(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'gaster')):
                    print('[*] Downloading gaster.....')
                    with zipfile.ZipFile(BytesIO(urllib.request.urlopen(urllib.request.Request('https://nightly.link/palera1n/gaster/workflows/makefile/main/gaster-{}.zip'.format(self.os_type), headers={'User-Agent': 'curl/7.85.0'})).read())) as gaster_zip:
                        gaster_zip.extractall(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type))+'/.')
                    print('[*] gaster Download Done!')
                pass
            self.return_path = os.getcwd()
            os.chdir(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type)))
            for chmd in sorted(os.listdir()):
                try:
                    os.chmod(chmd, 0o755)
                except:
                    continue
            os.chdir(self.return_path)
            self.sshrd_check = self.info('recovery', 'CPID')
            self.sshrd_replace = self.info('recovery', 'MODEL')
            self.sshrd_deviceid = self.info('recovery', 'PRODUCT')
            self.sshrd_device_check = '0'
            if self.os_type == 'Darwin':
                check_dfu_process = 'none'
                check_dfu = True
                while check_dfu:
                    while check_dfu_process == 'none':
                        try:
                            check_dfu_process = subprocess.Popen('system_profiler SPUSBDataType', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode()
                            break
                        except:
                            check_dfu_process = 'none'
                            time.sleep(0.5)
                    if re.compile('.+(DFU Mode).+').search(check_dfu_process):
                        check_dfu = False
                        break
                    else:
                        print("[*] Waiting for device in DFU mode", end='\r', flush=True)
                        time.sleep(1)
                        check_dfu = True
                pass
            if self.os_type == 'Linux':
                check_dfu_process = 'none'
                check_dfu = True
                while check_dfu:
                    while check_dfu_process == 'none':
                        try:
                            check_dfu_process = subprocess.Popen('lsusb', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode()
                            break
                        except:
                            check_dfu_process = 'none'
                            time.sleep(0.5)
                    if re.compile('.+(DFU Mode).+').search(check_dfu_process):
                        check_dfu = False
                        break
                    else:
                        print("[*] Waiting for device in DFU mode", end='\r', flush=True)
                        time.sleep(1)
                        check_dfu = True
            if os.path.exists(os.path.join(self.default_path, 'ramdisk_work')):
                shutil.rmtree(os.path.join(self.default_path, 'ramdisk_work'))
            os.makedirs('sshramdisk', exist_ok=True)
            os.makedirs('ramdisk_work', exist_ok=True)
            subprocess.run('{} pwn'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'gaster')), shell=True)
            subprocess.run('{} -e -s {} -m {}'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'img4tool'), os.path.join('ramdisk_shsh', '{}.shsh'.format(self.sshrd_check)), os.path.join('ramdisk_work', 'IM4M')), shell=True)
            os.chdir(os.path.join(self.default_path, 'ramdisk_work'))
            subprocess.run('{} -g BuildManifest.plist {}'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'pzb'), self.ipsw_url), shell=True)
            try:
                BuildManifest = open('BuildManifest.plist', 'r').read()
            except:
                BuildManifest = open('BuildManifest.plist', 'rb').read().decode()
            subprocess.run('{} -g {} {}'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'pzb'), re.sub('<.*?[string]>', '', re.search('.+[{}].*iBSS[.].*'.format(self.sshrd_replace), BuildManifest).group()).replace('\t','').replace('/', os.sep), self.ipsw_url), shell=True)
            subprocess.run('{} -g {} {}'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'pzb'), re.sub('<.*?[string]>', '', re.search('.+[{}].*iBEC[.].*'.format(self.sshrd_replace), BuildManifest).group()).replace('\t','').replace('/', os.sep), self.ipsw_url), shell=True)
            subprocess.run('{} -g {} {}'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'pzb'), re.sub('<.*?[string]>', '', re.search('.+[{}].*DeviceTree[.].*'.format(self.sshrd_replace), BuildManifest).group()).replace('\t','').replace('/', os.sep), self.ipsw_url), shell=True)
            if self.os_type == 'Darwin':
                plutil_stdout = subprocess.Popen('/usr/bin/plutil -extract "BuildIdentities".0."Manifest"."RestoreRamDisk"."Info"."Path" xml1 -o - BuildManifest.plist', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode()
                subprocess.run('{} -g {} {}'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'pzb'), os.path.join('Firmware', '{}.trustcache'.format(re.sub('(<.*?[string]>)', '', plutil_stdout.split('<string>')[-1].replace('\n', '')))), self.ipsw_url), shell=True)
            if self.os_type == 'Linux':
                plist_buddy_stdout = subprocess.Popen('{} BuildManifest.plist -c "Print BuildIdentities:0:Manifest:RestoreRamDisk:Info:Path"'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'PlistBuddy')), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode()
                subprocess.run('{} -g {} {}'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'pzb'), os.path.join('Firmware', '{}.trustcache'.format(plist_buddy_stdout.replace('"', ''))), self.ipsw_url), shell=True)
            subprocess.run('{} -g {} {}'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'pzb'), re.sub('<.*?[string]>', '', re.search('.*kernelcache.release[.].*', BuildManifest).group()).replace('\t',''), self.ipsw_url), shell=True)
            if self.os_type == 'Darwin':
                plutil_stdout2 = subprocess.Popen('/usr/bin/plutil -extract "BuildIdentities".0."Manifest"."RestoreRamDisk"."Info"."Path" xml1 -o - BuildManifest.plist', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode()
                subprocess.run('{} -g {} {}'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'pzb'), re.sub('(<.*?[string]>)', '', plutil_stdout2.split('<string>')[-1].replace('\n', '')), self.ipsw_url), shell=True)
            if self.os_type == 'Linux':
                plist_buddy_stdout2 = subprocess.Popen('{} BuildManifest.plist -c "Print BuildIdentities:0:Manifest:RestoreRamDisk:Info:Path"'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'PlistBuddy')), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode()
                subprocess.run('{} -g {} {}'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'pzb'), plist_buddy_stdout2.replace('"', ''), self.ipsw_url), shell=True)
            os.chdir(self.default_path)
            subprocess.run('{} decrypt {} {}'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'gaster'), os.path.join('ramdisk_work', re.sub('<.*?[string]>', '', re.search('.+[{}].*iBSS[.].*'.format(self.sshrd_replace), BuildManifest).group()).replace('\t','').split('/')[-1]), os.path.join('ramdisk_work', 'iBSS.dec')), shell=True)
            subprocess.run('{} decrypt {} {}'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'gaster'), os.path.join('ramdisk_work', re.sub('<.*?[string]>', '', re.search('.+[{}].*iBEC[.].*'.format(self.sshrd_replace), BuildManifest).group()).replace('\t','').split('/')[-1]), os.path.join('ramdisk_work', 'iBEC.dec')), shell=True)
            subprocess.run('%s %s %s' % (os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'iBoot64Patcher'), os.path.join('ramdisk_work', 'iBSS.dec'), os.path.join('ramdisk_work', 'iBSS.patched')), shell=True)
            subprocess.run('%s -i %s -o %s -M %s -A -T ibss' % (os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'img4'), os.path.join('ramdisk_work', 'iBSS.patched'), os.path.join('sshramdisk', 'iBSS.img4'), os.path.join('ramdisk_work', 'IM4M')), shell=True)
            option_check = '0'
            if self.sshrd_check == '0x8960':
                option_check = '1'
            if self.sshrd_check == '0x7000':
                option_check = '1'
            if self.sshrd_check == '0x7001':
                option_check
            if option_check == '1':
                subprocess.run('%s %s %s -b "rd=md0 debug=0x2014e wdt=-1 -restore" -n' % (os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'iBoot64Patcher'), os.path.join('ramdisk_work', 'iBEC.dec'), os.path.join('ramdisk_work', 'iBEC.patched')), shell=True)
            else:
                subprocess.run('%s %s %s -b "rd=md0 debug=0x2014e wdt=-1" -n' % (os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'iBoot64Patcher'), os.path.join('ramdisk_work', 'iBEC.dec'), os.path.join('ramdisk_work', 'iBEC.patched')), shell=True)
            subprocess.run('%s -i %s -o %s -M %s -A -T ibec' % (os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'img4'), os.path.join('ramdisk_work', 'iBEC.patched'), os.path.join('sshramdisk', 'iBEC.img4'), os.path.join('ramdisk_work', 'IM4M')), shell=True)
            subprocess.run('%s -i %s -o %s' % (os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'img4'), os.path.join('ramdisk_work', re.sub('<.*?[string]>', '', re.search('.*kernelcache.release[.].*', BuildManifest).group()).replace('\t','')), os.path.join('ramdisk_work', 'kcache.raw')), shell=True)
            subprocess.run('%s %s %s -a' % (os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'Kernel64Patcher'), os.path.join('ramdisk_work', 'kcache.raw'), os.path.join('ramdisk_work', 'kcache.patched')), shell=True)
            self.kerneldiff(os.path.join('ramdisk_work', 'kcache.raw'), os.path.join('ramdisk_work', 'kcache.patched'), os.path.join('ramdisk_work', 'kc.bpatch'))
            if self.os_type == 'Linux':
                subprocess.run('%s -i %s -o %s -M %s -T rkrn -P %s -J' % (os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'img4'), os.path.join('ramdisk_work', re.sub('<.*?[string]>', '', re.search('.*kernelcache.release[.].*', BuildManifest).group()).replace('\t','')), os.path.join('sshramdisk', 'kernelcache.img4'), os.path.join('ramdisk_work', 'IM4M'), os.path.join('ramdisk_work', 'kc.bpatch')), shell=True)
            if self.os_type == 'Darwin':
                subprocess.run('%s -i %s -o %s -M %s -T rkrn -P %s' % (os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'img4'), os.path.join('ramdisk_work', re.sub('<.*?[string]>', '', re.search('.*kernelcache.release[.].*', BuildManifest).group()).replace('\t','')), os.path.join('sshramdisk', 'kernelcache.img4'), os.path.join('ramdisk_work', 'IM4M'), os.path.join('ramdisk_work', 'kc.bpatch')), shell=True)
            subprocess.run('%s -i %s -o %s -M %s -T rdtr' % (os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'img4'), os.path.join('ramdisk_work', re.sub('<.*?[string]>', '', re.search('.+[{}].*DeviceTree[.].*'.format(self.sshrd_replace), BuildManifest).group()).replace('\t','').split('/')[-1]), os.path.join('sshramdisk', 'devicetree.img4'), os.path.join('ramdisk_work', 'IM4M')), shell=True)
            if self.os_type == 'Darwin':
                plutil_stdout3 = subprocess.Popen('/usr/bin/plutil -extract "BuildIdentities".0."Manifest"."RestoreRamDisk"."Info"."Path" xml1 -o - {}'.format(os.path.join('ramdisk_work', 'BuildManifest.plist')), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode()
                subprocess.run('{} -i {}.trustcache -o {} -M {} -T rtsc'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'img4'), re.sub('(<.*?[string]>)', '', plutil_stdout3.split('<string>')[-1].replace('\n', '')), os.path.join('sshramdisk', 'trustcache.img4'), os.path.join('ramdisk_work', 'IM4M')), shell=True)
                subprocess.run('{} -i {} -o {}'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'img4'), re.sub('(<.*?[string]>)', '', plutil_stdout3.split('<string>')[-1].replace('\n', '')), os.path.join('ramdisk_work', 'ramdisk.dmg')), shell=True)
            if self.os_type == 'Linux':
                plist_buddy_stdout3 = subprocess.Popen('{} BuildManifest.plist -c "Print BuildIdentities:0:Manifest:RestoreRamDisk:Info:Path"'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'PlistBuddy')), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode()
                subprocess.run('{} -i {}.trustcache -o {} -M {} -T rtsc'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'img4'), os.path.join('ramdisk_work', plist_buddy_stdout3.replace('"', '')), os.path.join('sshramdisk', 'trustcache.img4'), os.path.join('ramdisk_work', 'IM4M')), shell=True)
                subprocess.run('{} -i {} -o {}'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'img4'), os.path.join('ramdisk_work', plist_buddy_stdout3.replace('"', '')), os.path.join('ramdisk_work', 'ramdisk.dmg')), shell=True)
            if self.os_type == 'Darwin':
                subprocess.run('hdiutil resize -size 256MB work/ramdisk.dmg', shell=True)
                subprocess.run('hdiutil attach -mountpoint /tmp/SSHRD {}'.format(os.path.join('ramdisk_work', 'ramdisk.dmg')), shell=True)
                subprocess.run('{} -x --no-overwrite-dir -f {} -C /tmp/SSHRD/'.format(os.path.join('ramdisk_other', 'ramdisk.tar.gz')), shell=True)
                if not arg2 == 'rootless':
                    with zipfile.ZipFile(os.path.join('ramdisk_Pogo', 'Pogo.zip'), 'r') as pogo_ipa:
                        pogo_ipa.extractall(os.path.join('ramdisk_work', 'Pogo')+'/.')
                    with zipfile.ZipFile(os.path.join('ramdisk_work', 'Pogo', 'Pogo.ipa'), 'r') as pogo:
                        pogo.extractall(os.path.join('ramdisk_work', 'Pogo', 'Pogo')+'/.')
                    try:
                        shutil.rmtree('/tmp/SSHRD/usr/local/bin/loader.app')
                    except:
                        pass
                    try:
                        shutil.copytree(os.path.join('ramdisk_work', 'Pogo', 'Pogo', 'Payload', 'Pogo.app'), '/tmp/SSHRD/usr/local/bin/loader.app')
                    except:
                        pass
                    os.rename('/tmp/SSHRD/usr/local/bin/loader.app/Pogo', '/tmp/SSHRD/usr/local/bin/loader.app/Tips')
                subprocess.run('hdiutil detach -force /tmp/SSHRD', shell=True)
                subprocess.run('hdiutil resize -sectors min {}'.format(os.path.join('ramdisk_work', 'ramdisk.dmg')), shell=True)
            if os_type == 'Linux':
                if os.path.exists(os.path.join('ramdisk_other', 'ramdisk.tar.gz')):
                    with tarfile.open(os.path.join('ramdisk_other', 'ramdisk.tar.gz'), 'r:gz') as ramdisk_tar:
                        ramdisk_tar.extractall(path='ramdisk_other/.')
                    subprocess.run('{} {} grow 300000000'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'hfsplus'), os.path.join('ramdisk_work', 'ramdisk.dmg')), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    subprocess.run('{} {} untar {}'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'hfsplus'), os.path.join('ramdisk_work', 'ramdisk.dmg'), os.path.join('ramdisk_other', 'ramdisk.tar')), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if not arg2 == 'rootless':
                        with zipfile.ZipFile(os.path.join('ramdisk_Pogo', 'Pogo.zip'), 'r') as pogo_ipa:
                            pogo_ipa.extractall(os.path.join('ramdisk_work', 'Pogo')+'/.')
                        with zipfile.ZipFile(os.path.join('ramdisk_work', 'Pogo', 'Pogo.ipa'), 'r') as pogo:
                            pogo.extractall(os.path.join('ramdisk_work', 'Pogo', 'Pogo')+'/.')
                        os.makedirs(os.path.join('ramdisk_work', 'Pogo', 'uwu', 'usr', 'local', 'bin'), exist_ok=True)
                        shutil.copytree(os.path.join('ramdisk_work', 'Pogo', 'Pogo', 'Payload', 'Pogo.app'), os.path.join('ramdisk_work', 'Pogo', 'uwu', 'usr', 'local', 'bin', 'loader.app'))
                        subprocess.run('{} {} rmall usr/local/bin/loader.app'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'hfsplus'), os.path.join('ramdisk_work', 'ramdisk.dmg')), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        subprocess.run('{} {} addall {}'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'hfsplus'), os.path.join('ramdisk_work', 'ramdisk.dmg'), os.path.join('ramdisk_work', 'Pogo', 'uwu')), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        subprocess.run('{} {} mv /usr/local/bin/loader.app/Pogo /usr/local/bin/loader.app/Tips'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'hfsplus'), os.path.join('ramdisk_work', 'ramdisk.dmg')), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                pyimg4(['im4p', 'create', '-i', '{}'.format(os.path.join('ramdisk_work', 'ramdisk.dmg')), '-o', '{}'.format(os.path.join('ramdisk_work', 'ramdisk.im4p')), '-f', 'rdsk'])
            except SystemExit:
                pass
            try:
                pyimg4(['img4', 'create', '-p', '{}'.format(os.path.join('ramdisk_work', 'ramdisk.im4p')), '-m', '{}'.format(os.path.join('ramdisk_work', 'IM4M')), '-o', '{}'.format(os.path.join('sshramdisk', 'ramdisk.img4'))])
            except SystemExit:
                pass
            subprocess.run('{} -i {} -o {} -M {} -A -T rlgo'.format(os.path.join(self.default_path, 'ramdisk_{}'.format(self.os_type), 'img4'), os.path.join('ramdisk_other', 'bootlogo.im4p'), os.path.join('sshramdisk', 'bootlogo.img4'), os.path.join('ramdisk_work', 'IM4M')), shell=True)
            shutil.rmtree('ramdisk_work')
            return
        return

    def option_confirm(self):
        ans = {'y':True, 'yes':True, 'n':False, 'no':False}
        while True:
            try:
                return ans[input(colorama.Fore.RED + '[!] "--force-create-fakefs" Option is Very Dangerous Option! Do you continue OK? [N/y] ' + colorama.Fore.RESET).lower()]
            except KeyboardInterrupt:
                sys.exit(0)
            except SystemExit:
                sys.exit(0)
            except:
                print('[!] Input try again!')
                pass

    def main(self):
        self.palera1n_OS_check = '0'
        if self.os_type == 'Darwin':
            self.palera1n_OS_check = '1'
            subprocess.run('defaults write -g ignore-devices -bool true', shell=True)
            subprocess.run('defaults write com.apple.AMPDevicesAgent dontAutomaticallySyncIPods -bool true', shell=True)
            subprocess.run('killall Finder', shell=True)
            pass
        if self.os_type == 'Linux':
            self.palera1n_OS_check = '1'
            pass
        if self.os_type == 'Windows':
            print('[!] palera1n supported OS is Linux and MacOS only.')
            sys.exit(0)
        if self.palera1n_OS_check == '1':
            # Download Gaster.
            if not os.path.exists(os.path.join(self.binary_path, 'gaster')):
                print('[*] Downloading gaster.....')
                with zipfile.ZipFile(BytesIO(urllib.request.urlopen(urllib.request.Request('https://nightly.link/palera1n/gaster/workflows/makefile/main/gaster-{}.zip'.format(self.os_type), headers={'User-Agent': 'curl/7.85.0'})).read()), 'r') as gaster_zip:
                    gaster_zip.extractall(self.binary_path+'/.')
                print('[*] gaster Download Done!')
            # submodule update.
            subprocess.run('git submodule update --init --recursive', shell=True)
            if os.path.exists(os.path.join(self.default_path, 'palera1n_work')):
                shutil.rmtree(os.path.join(self.default_path, 'palera1n_work'))
                os.makedirs(os.path.join(self.default_path, 'palera1n_work'), exist_ok=True)
            else:
                os.makedirs(os.path.join(self.default_path, 'palera1n_work'), exist_ok=True)
            os.chdir(self.binary_path)
            for auth in sorted(os.listdir()):
                try:
                    os.chmod(auth, 0o755) # chmod +x Binarys/*
                except:
                    pass
            os.chdir(self.default_path)
            # show logo
            print('palera1n | Version {}-{}-{}\nWritten by Nebula and Mineek | Some code and ramdisk from Nathan | Loader app by Amy\n'.format(self.version, self.git_branch, self.git_commit))
            if self.clean_option == '1':
                for clean_dir in sorted(os.listdir(self.default_path)):
                    if 'boot' in clean_dir:
                        try:
                            shutil.rmtree(clean_dir)
                        except:
                            continue
                    if clean_dir == 'palera1n_work':
                        try:
                            shutil.rmtree(clean_dir)
                        except:
                            continue
                    if clean_dir == '.tweaksinstalled':
                        if os.path.isdir(clean_dir):
                            try:
                                shutil.rmtree(clean_dir)
                            except:
                                continue
                        if os.path.isfile(clean_dir):
                            try:
                                os.remove(clean_dir)
                            except:
                                continue
            if self.tweak_option == '0' and self.semi_tethered_option == '1':
                print('[!] --semi-tethered may not be used with rootless\n    Rootless is already semi-tethered')
                sys.exit(1)
            if self.tweak_option == '1' and not os.path.exists('.tweaksinstalled') and not os.path.exists('.disclaimeragree') and self.semi_tethered_option == '0' and self.restorerootfs_option == '0':
                print("!!! WARNING WARNING WARNING !!!")
                print("This flag will add tweak support BUT WILL BE TETHERED.")
                print("THIS ALSO MEANS THAT YOU'LL NEED A PC EVERY TIME TO BOOT.")
                print("THIS ONLY WORKS ON 15.0-15.7.1")
                print("DO NOT GET ANGRY AT US IF UR DEVICE IS BORKED, IT'S YOUR OWN FAULT AND WE WARNED YOU")
                if input("DO YOU UNDERSTAND? TYPE 'Yes, do as I say' TO CONTINUE\n") == 'Yes, do as I say':
                    print("Are you REALLY sure? WE WARNED YOU!")
                    if input("Type 'Yes, I am sure' to continue\n") == 'Yes, I am sure':
                        print('[*] Enabling tweaks')
                        with open('.disclaimeragree', 'w') as a:
                            a.write('')
            print('[*] Waiting for devices')
            while self.get_device_mode() == 'none':
                time.sleep(1)
            print('[*] Detected {} mode device'.format(self.get_device_mode().upper()))
            if re.compile('(pongo|checkra1n_stage2|diag)').search(self.get_device_mode()):
                print('[-] Detected device in unsupported mode {}'.format(self.get_device_mode()))
                sys.exit(1)
            if not self.get_device_mode() == 'normal' and self.ramdisk == '' and not self.DFUHelper_option == '1':
                print("[-] You must pass the version your device is on when not starting from normal mode")
                sys.exit(1)
            if self.get_device_mode() == 'ramdisk':
                self.kill_if_running('iproxy')
                print('[*] Rebooting device in SSH Ramdisk')
                if self.os_type == 'Linux':
                    threading.Thread(target=self.starting_root_iproxy, daemon=True).start()
                    pass
                if self.os_type == 'Darwin':
                    threading.Thread(target=self.starting_iproxy, daemon=True).start()
                    pass
                time.sleep(1)
                self.remote_command_sender('/usr/sbin/nvram auto-boot=false')
                self.remote_command_sender('/sbin/reboot')
                self.kill_if_running('iproxy')
                self.wait('recovery')
                pass
            if self.get_device_mode() == 'normal':
                self.iDeviceVersion = self.info('normal', 'ProductVersion')
                self.iDeviceArch = self.info('normal', 'CPUArchitecture')
                if self.iDeviceArch == 'arm64e':
                    print("[-] palera1n doesn't, and never will, work on non-checkm8 devices")
                    sys.exit(1)
                else:
                    print('Hello, {} on {}'.format(self.info('normal', 'ProductType'), self.iDeviceVersion))
                    print('[*] Switching device into recovery mode...')
                    subprocess.run('{} {}'.format(os.path.join(self.binary_path, 'ideviceenterrecovery'), self.info('normal', 'UniqueDeviceID')), shell=True)
                    self.wait('recovery')
                    pass
            self.cpid = self.info('recovery', 'CPID')
            self.model = self.info('recovery', 'MODEL')
            self.device_id = self.info('recovery', 'PRODUCT')
            if self.DFUHelper_option == '1':
                print('[*] Running DFU helper')
                self.dfuhelper(self.cpid)
            if self.ipsw_url == '':
                if re.compile('.*iPad.*').search(self.device_id):
                    self.deviceOS = 'iPadOS'
                    self.iDeviceType = 'iPad'
                elif re.compile('.*iPod.*').search(self.device_id):
                    self.deviceOS = 'iOS'
                    self.iDeviceType = 'iPod'
                else:
                    self.deviceOS = 'iOS'
                    self.iDeviceType = 'iPhone'
                self.buildid = list(set([x['buildid'] for x in json.loads(json.dumps(ast.literal_eval(str(json.loads(urllib.request.urlopen(urllib.request.Request('https://api.ipsw.me/v4/ipsw/{}'.format(self.ramdisk), headers={'User-Agent': 'curl/7.85.0'})).read()))))) if self.iDeviceType in x['identifier']]))[0]
                if self.buildid == '19B75':
                    self.buildid = '19B74'
                self.ipsw_url = json.loads(urllib.request.urlopen(urllib.request.Request('https://api.appledb.dev/ios/{};{}.json'.format(self.deviceOS, self.buildid), headers={'User-Agent': 'curl/7.85.0'})).read())['devices'][self.device_id]['ipsw']
            if self.restorerootfs_option == '1':
                os.remove(os.path.join(self.default_path, 'blobs', '{}-{}.shsh2'.format(self.device_id, self.ramdisk)))
                shutil.rmtree(os.path.join(self.default_path, 'boot-{}'.format(self.device_id)))
                shutil.rmtree(os.path.join(self.default_path, 'palera1n_work'))
                if os.path.isfile(os.path.join(self.default_path, '.tweaksinstalled')):
                    try:
                        os.remove(os.path.join(self.default_path, '.tweaksinstalled'))
                    except:
                        pass
                elif os.path.isdir(os.path.join(self.default_path, '.tweaksinstalled')):
                    try:
                        shutil.rmtree(os.path.join(self.default_path, '.tweaksinstalled'))
                    except:
                        pass
            if not self.get_device_mode() == 'dfu':
                self.recovery_fix_auto_boot()
                if not self.dfuhelper(self.cpid) == 0:
                    print("[-] failed to enter DFU mode, run palera1n.sh again")
                    sys.exit(1)
            time.sleep(2)
            # Ramdisk
            if not os.path.exists(os.path.join(self.default_path, 'blobs', '{}-{}.shsh2'.format(self.device_id, self.ramdisk))):
                os.makedirs(os.path.join(self.default_path, 'blobs'), exist_ok=True)
                if self.tweak_option == '0':
                    self.sshrd_arg2 = 'rootless'
                if self.tweak_option == '1':
                    self.sshrd_arg2 = ''
                self.sshrd_sh('15.4', self.sshrd_arg2)
                print("[*] Booting ramdisk")
                self.sshrd_sh('boot', self.sshrd_arg2)
                if os.path.exists('~/.ssh/known_hosts'):
                    if self.os_type == 'Darwin':
                        self.founds = '0'
                        self.known_hosts = open('~/.ssh/known_hosts', 'r').read()
                        if re.compile('localhost').search(self.known_hosts):
                            self.founds = '1'
                            self.fixed_data = re.sub('(.*localhost).+\n', '', self.known_hosts)
                        if re.compile('127.0.0.1').search(self.known_hosts):
                            self.founds = '1'
                            self.fixed_data = re.sub('.*(127\.0\.0\.1).+\n', '', self.known_hosts)
                        if self.founds == '1':
                            with open('~/.ssh/known_hosts.bak', 'w') as bak:
                                bak.write(self.known_hosts)
                            with open('~/.ssh/known_hosts', 'w') as fixed:
                                fixed.write(self.fixed_data)
                    if self.os_type == 'Linux':
                        self.founds = '0'
                        self.known_hosts = open('~/.ssh/known_hosts', 'r').read()
                        if re.compile('localhost').search(self.known_hosts):
                            self.founds = '1'
                            self.fixed_data = re.sub('(.*localhost).+\n', '', self.known_hosts)
                        if re.compile('127.0.0.1').search(self.known_hosts):
                            self.founds = '1'
                            self.fixed_data = re.sub('.*(127\.0\.0\.1).+\n', '', self.known_hosts)
                        if self.founds == '1':
                            with open('~/.ssh/known_hosts.bak', 'w') as bak:
                                bak.write(self.known_hosts)
                if self.os_type == 'Linux':
                    threading.Thread(target=self.starting_root_iproxy, daemon=True).start()
                    pass
                if self.os_type == 'Darwin':
                    threading.Thread(target=self.starting_iproxy, daemon=True).start()
                    pass
                while self.remote_command_sender('echo connected') == '':
                    time.sleep(1)
                if self.no_baseband_option == '0':
                    print("[*] Testing for baseband presence")
                    if self.remote_command_sender("/usr/bin/mgask HasBaseband | grep -E 'true|false'") == 'true' and re.compile('.*0x7001.*').search(self.cpid):
                        self.default_disk_numbar = 7
                    elif self.remote_command_sender("/usr/bin/mgask HasBaseband | grep -E 'true|false'") == 'false':
                        if re.compile('.*0x7001.*').search(self.cpid):
                            self.default_disk_numbar = 6
                        else:
                            self.default_disk_numbar = 7
                self.remote_command_sender('/usr/bin/mount_filesystems')
                self.has_active = self.remote_command_sender('ls /mnt6/active')
                if not self.has_active == '/mnt6/active':
                    print("[!] Active file does not exist! Please use SSH to create it")
                    print("    /mnt6/active should contain the name of the UUID in /mnt6")
                    print("    When done, type reboot in the SSH session, then rerun the script")
                    print("    ssh root@localhost -p 2222")
                    sys.exit(0)
                self.active = self.remote_command_sender('cat /mnt6/active')
                if self.restorerootfs_option == '1':
                    print("[*] Removing Jailbreak")
                    self.remote_command_sender('/sbin/apfs_deletefs disk0s1s{} > /dev/null || true'.format(self.default_disk_numbar))
                    self.remote_command_sender('rm -f /mnt2/jb')
                    self.remote_command_sender('rm -rf /mnt2/cache /mnt2/lib')
                    self.remote_command_sender('rm -f /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kcache.raw /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kcache.patched /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kcache.im4p /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kernelcachd'.format(self.active, self.active, self.active, self.active))
                    if self.semi_tethered_option == '0':
                        self.remote_command_sender('mv /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kernelcache.bak /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kernelcache'.format(self.active, self.active))('mv /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kernelcache.bak /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kernelcache'.format(self.active, self.active))
                    self.remote_command_sender('/bin/sync')
                    self.remote_command_sender('/usr/sbin/nvram auto-boot=true')
                    try:
                        os.remove('BuildManifest.plist')
                    except:
                        pass
                    print("[*] Done! Rebooting your device")
                    self.remote_command_sender('/sbin/reboot')
                print("[*] Dumping blobs and installing Pogo")
                time.sleep(1)
                try:
                    with open('cat_data', 'w') as cat:
                        cat.write(self.remote_command_sender('cat /dev/rdisk1'))
                except:
                    with open('cat_data', 'wb') as cat:
                        cat.write(self.remote_command_sender('cat /dev/rdisk1'))
                counts = subprocess.Popen('echo $((0x4000))', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode()
                subprocess.run('dd if=cat_data of=dump.raw bs=256 count={}'.format(counts), shell=True)
                try:
                    os.remove('cat_data')
                except:
                    pass
                subprocess.run('{} --convert -s {} dump.raw'.format(os.path.join(self.binary_path, 'img4tool'), os.path.join('blobs', '{}-{}.shsh2'.format(self.device_id, self.ramdisk))))
                try:
                    os.remove('dump.raw')
                except:
                    pass
                if self.semi_tethered_option == '1' and self.skip_fakefs_option == '0':
                    print("[*] Creating fakefs, this may take a while (up to 10 minutes)")
                    error_count = 0
                    if self.force_createfs_option == '1':
                        if remote_command_sender('/sbin/newfs_apfs -A -D -v System /dev/disk0s1')[0:11] == 'newfs_apfs:':
                            error_count += 1
                    else:
                        if self.remote_command_sender('/sbin/newfs_apfs -A -D -o role=r -v System /dev/disk0s1')[0:11] == 'newfs_apfs:':
                            error_count += 1
                    time.sleep(2)
                    if self.remote_command_sender('/sbin/mount_apfs /dev/disk0s1s${disk} /mnt8')[0:11] == 'mount_apfs:':
                        error_count += 1
                    time.sleep(1)
                    if 'cp: ' in self.remote_command_sender('cp -a /mnt1/. /mnt8/'):
                        error_count += 1
                    time.sleep(1)
                    print("[*] fakefs created, continuing...")
                    if 2 <= error_count:
                        print("[*] Using the old fakefs, run restorerootfs if you need to clean it")
                        sys.exit(1)
                if self.no_install_option == '0':
                    self.Tipsdir = self.remote_command_sender("/usr/bin/find /mnt2/containers/Bundle/Application/ -name 'Tips.app'")
                    time.sleep(1)
                    if self.Tipsdir == '':
                        print("[!] Tips is not installed. Once your device reboots, install Tips from the App Store and retry")
                        self.remote_command_sender('/sbin/reboot')
                        time.sleep(1)
                        self.kill_if_running('iproxy')
                        sys.exit(0)
                    self.remote_command_sender('/bin/mkdir -p /mnt1/private/var/root/temp')
                    time.sleep(1)
                    self.remote_command_sender('/bin/cp -r /usr/local/bin/loader.app/* /mnt1/private/var/root/temp')
                    time.sleep(1)
                    self.remote_command_sender('/bin/rm -rf /mnt1/private/var/root/temp/Info.plist /mnt1/private/var/root/temp/Base.lproj /mnt1/private/var/root/temp/PkgInfo')
                    time.sleep(1)
                    self.remote_command_sender('/bin/cp -rf /mnt1/private/var/root/temp/* {}'.format(self.Tipsdir))
                    time.sleep(1)
                    self.remote_command_sender('/bin/rm -rf /mnt1/private/var/root/temp')
                    time.sleep(1)
                    self.remote_command_sender('/usr/sbin/chown 33 {}/Tips'.format(self.Tipsdir))
                    time.sleep(1)
                    self.remote_command_sender('/bin/chmod 755 {}/Tips {}/PogoHelper'.format(self.Tipsdir, self.Tipsdir))
                    time.sleep(1)
                    self.remote_command_sender('/usr/sbin/chown 0 {}/PogoHelper'.format(self.Tipsdir))
                    pass
                if self.semi_tethered_option == '1':
                    self.remote_command_sender('/usr/sbin/nvram auto-boot=true')
                else:
                    self.remote_command_sender('/usr/sbin/nvram auto-boot=false')
                self.remote_cp('binaries/Kernel15Patcher.ios root@localhost:/mnt1/private/var/root/Kernel15Patcher.ios')
                self.remote_command_sender('/usr/sbin/chown 0 /mnt1/private/var/root/Kernel15Patcher.ios')
                self.remote_command_sender('/bin/chmod 755 /mnt1/private/var/root/Kernel15Patcher.ios')
                print("[*] Patching the kernel")
                self.remote_command_sender('rm -f /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kcache.raw /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kcache.patched /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kcache.im4p /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kernelcachd'.format(self.active, self.active, self.active, self.active))
                if self.semi_tethered_option == '1':
                    self.remote_command_sender('cp /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kernelcache /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kernelcache.bak'.format(self.active, self.active))
                else:
                    self.remote_command_sender('mv /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kernelcache /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kernelcache.bak'.format(self.active, self.active))
                time.sleep(1)
                print("[*] Downloading BuildManifest")
                subprocess.run('{} -g BuildManifest.plist {}'.format(os.path.join(self.binary_path, 'pzb'), self.ipsw_url), shell=True)
                BuildManifest = open('BuildManifest.plist', 'rb').read().decode()
                print("[*] Downloading kernelcache")
                subprocess.run('{} -g "{}" "{}"'.format(os.path.join(self.binary_path, 'pzb'), re.sub('<.*?[string]>', '', re.search('.*kernelcache.release[.].*', BuildManifest).group()).replace('\t',''), self.ipsw_url), shell=True)
                shutil.move(re.sub('<.*?[string]>', '', re.search('.*kernelcache.release[.].*', BuildManifest).group()).replace('\t',''), os.path.join(self.default_path, 'palera1n_work', 'kernelcache'))
                dev_found = '0'
                if re.compile('iPhone8.*').search(self.device_id):
                    dev_found = '1'
                if re.compile('iPad6.*').search(self.device_id):
                    dev_found = '1'
                if re.compile('.*iPad5.*').search(self.device_id):
                    dev_found = '1'
                if dev_found == '1':
                    try:
                        pyimg4(['im4p', 'extract', '-i', '{}'.format(os.path.join(self.default_path, 'palera1n_work', 'kernelcache')), '-o', '{}'.format(os.path.join(self.default_path, 'palera1n_work', 'kcache.raw')), '--extra', '{}'.format(os.path.join(self.default_path, 'palera1n_work', 'kpp.bin'))])
                    except SystemExit:
                        pass
                else:
                    try:
                        pyimg4(['im4p', 'extract', '-i', '{}'.format(os.path.join(self.default_path, 'palera1n_work', 'kernelcache')), '-o', '{}'.format(os.path.join(self.default_path, 'palera1n_work', 'kcache.raw'))])
                    except SystemExit:
                        pass
                time.sleep(1)
                self.remote_cp('{} root@localhost:/mnt6/{}/System/Library/Caches/com.apple.kernelcaches/'.format(os.path.join(self.default_path, 'palera1n_work', 'kcache.im4p'), self.active))
                self.remote_command_sender('/mnt1/private/var/root/Kernel15Patcher.ios /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kcache.raw /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kcache.patched'.format(self.active, self.active))
                self.remote_cp('root@localhost:/mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kcache.patched {}'.format(self.active, os.path.join(self.default_path, 'palera1n_work')))
                subprocess.run('{} {} {} -e'.format(os.path.join(self.binary_path, 'Kernel64Patcher'), os.path.join(self.default_path, 'palera1n_work', 'kcache.patched'), os.path.join(self.default_path, 'palera1n_work', 'kcache.patched2')))
                time.sleep(1)
                dev_found2 = '0'
                if re.compile('.*iPhone8.*').search(self.device_id):
                    dev_found2 = '1'
                if re.compile('.*iPad6.*').search(self.device_id):
                    dev_found2 = '1'
                if re.compile('.*iPad5.*').search(self.device_id):
                    dev_found2 = '1'
                if dev_found2 == '1':
                    try:
                        pyimg4(['im4p', 'create', '-i', '{}'.format(os.path.join(self.default_path, 'palera1n_work', 'kcache.patched2')), '-o', '{}'.format(os.path.join(self.default_path, 'palera1n_work', 'kcache.im4p')), '-f', 'krnl', '--extra', '{}'.format(os.path.join(self.default_path, 'palera1n_work', 'kpp.bin')), '--lzss'])
                    except SystemExit:
                        pass
                else:
                    try:
                        pyimg4(['im4p', 'create', '-i', '{}'.format(os.path.join(self.default_path, 'palera1n_work', 'kcache.patched2')), '-o', '{}'.format(os.path.join(self.default_path, 'palera1n_work', 'kcache.im4p')), '-f', 'krnl', '--lzss'])
                    except SystemExit:
                        pass
                time.sleep(1)
                self.remote_cp('{} root@localhost:/mnt6/{}/System/Library/Caches/com.apple.kernelcaches/'.format(os.path.join(self.default_path, 'palera1n_work', 'kcache.im4p'), self.active))
                self.remote_command_sender('img4 -i /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kcache.im4p -o /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kernelcachd -M /mnt6/{}/System/Library/Caches/apticket.der'.format(self.active, self.active, self.active))
                self.remote_command_sender('rm -f /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kcache.raw /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kcache.patched /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kcache.im4p'.format(self.active, self.active, self.active))
                time.sleep(1)
                self.has_kernelcachd = self.remote_command_sender('ls /mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kernelcachd'.format(self.active))
                if self.has_kernelcachd == '/mnt6/{}/System/Library/Caches/com.apple.kernelcaches/kernelcachd'.format(self.active):
                    print("[*] Custom kernelcache now exists!")
                else:
                    print("[!] Custom kernelcache doesn't exist..? Please send a log and report this bug...")
                shutil.rmtree(os.path.join(self.default_path, 'palera1n_work'))
                os.makedirs(os.path.join(self.default_path, 'palera1n_work'), exist_ok=True)
                time.sleep(2)
                print("[*] Done! Rebooting your device")
                self.remote_command_sender('/sbin/reboot')
                time.sleep(1)
                self.kill_if_running('iproxy')
                if self.semi_tethered_option == '1':
                    self.wait('normal')
                    time.sleep(5)
                    print("[*] Switching device into recovery mode...")
                    subprocess.run('{} {}'.format(os.path.join(self.binary_path, 'ideviceenterrecovery'), self.info('normal', 'UniqueDeviceID')), shell=True)
                elif self.tweak_option == '1':
                    self.wait('normal')
                    time.sleep(5)
                    print("[*] Switching device into recovery mode...")
                    subprocess.run('{} {}'.format(os.path.join(self.binary_path, 'ideviceenterrecovery'), self.info('normal', 'UniqueDeviceID')), shell=True)
                self.wait('recovery')
                self.dfuhelper(self.cpid)
                time.sleep(2)
                pass
            # Boot Create
            if not os.path.exists(os.path.join(self.default_path, 'boot-{}'.format(self.device_id), '.local')):
                shutil.rmtree(os.path.join(self.default_path, 'boot-{}'.format(self.device_id)))
            if not os.path.exists(os.path.join(self.default_path, 'boot-{}'.format(self.device_id), 'ibot.img4')):
                shutil.rmtree(os.path.join(self.default_path, 'boot-{}'.format(self.device_id)))
                os.makedirs(os.path.join(self.default_path, 'boot-{}'.format(self.device_id)), exist_ok=True)
                print("[*] Converting blob")
                subprocess.run('{} -e -s {} -m {}'.format(os.path.join(self.binary_path, 'img4tool'), os.path.join(self.default_path, 'blobs', '{}-{}.shsh2'.format(self.device_id, self.ramdisk)), os.path.join(self.default_path, 'palera1n_work', 'IM4M')), shell=True)
                os.chdir(os.path.join(self.default_path, 'palera1n_work'))
                print("[*] Downloading BuildManifest")
                subprocess.run('{} -g BuildManifest.plist {}'.format(os.path.join(self.binary_path, 'pzb'), self.ipsw_url), shell=True)
                try:
                    BuildManifest2 = open('BuildManifest.plist', 'r').read()
                except:
                    BuildManifest2 = open('BuildManifest.plist', 'rb').read().decode()
                print("[*] Downloading and decrypting iBSS")
                subprocess.run('{} -g {} {}'.format(os.path.join(self.binary_path, 'pzb'), re.sub('<.*?[string]>', '', re.search('.+[{}].*iBSS[.].*'.format(self.model), BuildManifest2).group()).replace('\t',''), self.ipsw_url), shell=True)
                subprocess.run('{} decrypt {} iBSS.dec'.format(os.path.join(self.binary_path, 'gaster'), re.sub('<.*?[string]>', '', re.search('.+[{}].*iBSS[.].*'.format(self.model), BuildManifest2).group()).replace('\t','').split('/')[-1]), shell=True)
                print("[*] Downloading and decrypting iBoot")
                subprocess.run('{} -g {} {}'.format(os.path.join(self.binary_path, 'pzb'), re.sub('<.*?[string]>', '', re.search('.+[{}].*iBoot[.].*'.format(self.model), BuildManifest2).group()).replace('\t',''), self.ipsw_url), shell=True)
                subprocess.run('{} decrypt {} ibot.dec'.format(os.path.join(self.binary_path, 'gaster'), re.sub('<.*?[string]>', '', re.search('.+[{}].*iBoot[.].*'.format(self.model), BuildManifest2).group()).replace('\t','').split('/')[-1]), shell=True)
                print("[*] Patching and signing iBSS/iBoot")
                subprocess.run('{} iBSS.dec iBSS.patched'.format(os.path.join(self.binary_path, 'iBoot64Patcher')), shell=True)
                if self.semi_tethered_option == '1':
                    if self.verbose_option == '1':
                        subprocess.run('{} ibot.dec ibot.patched -b "-v rd=disk0s1s{}" -l'.format(os.path.join(self.binary_path, 'iBoot64Patcher'), self.default_disk_numbar), shell=True)
                    else:
                        subprocess.run('{} ibot.dec ibot.patched -b "rd=disk0s1s{}" -l'.format(os.path.join(self.binary_path, 'iBoot64Patcher'), self.default_disk_numbar), shell=True)
                else:
                    if self.verbose_option == '1':
                        subprocess.run('{} ibot.dec ibot.patched -b "-v" -f'.format(os.path.join(self.binary_path, 'iBoot64Patcher')), shell=True)
                    else:
                        subprocess.run('{} ibot.dec ibot.patched -f'.format(os.path.join(self.binary_path, 'iBoot64Patcher')), shell=True)
                if self.os_type == 'Linux':
                    subprocess.run("sed -i 's/\/\kernelcache/\/\kernelcachd/g' ibot.patched", shell=True)
                if self.os_type == 'Darwin':
                    subprocess.run("LC_ALL=C sed -i.bak -e 's/s\/\kernelcache/s\/\kernelcachd/g' ibot.patched", shell=True)
                    subprocess.run('rm *.bak', shell=True)
                os.chdir(self.default_path)
                subprocess.run('{} -i {} -o {} -M {} -A -T ibss'.format(os.path.join(self.binary_path, 'img4'), os.path.join(self.default_path, 'palera1n_work', 'iBSS.patched'), os.path.join(self.default_path, 'boot-{}'.format(self.device_id), 'iBSS.img4'), os.path.join(self.default_path, 'palera1n_work', 'IM4M')), shell=True)
                if re.compile('.*0x801.*').search(self.cpid):
                    subprocess.run('{} -i {} -o {} -M {} -A -T ibss'.format(os.path.join(self.binary_path, 'img4'), os.path.join(self.default_path, 'palera1n_work', 'ibot.patched'), os.path.join(self.default_path, 'boot-{}'.format(self.device_id), 'ibot.img4'), os.path.join(self.default_path, 'palera1n_work', 'IM4M')), shell=True)
                else:
                    subprocess.run('{} -i {} -o {} -M {} -A -T ibec'.format(os.path.join(self.binary_path, 'img4'), os.path.join(self.default_path, 'palera1n_work', 'ibot.patched'), os.path.join(self.default_path, 'boot-{}'.format(self.device_id), 'ibot.img4'), os.path.join(self.default_path, 'palera1n_work', 'IM4M')), shell=True)
                with open(os.path.join('boot-{}'.format(self.device_id), '.local'), 'w') as touch:
                    touch.write('')
                pass
            # boot device
            time.sleep(2)
            self.pwn()
            self.reset()
            print("[*] Booting device")
            if re.compile('.*0x801.*').search(self.cpid):
                time.sleep(1)
                subprocess.run('{} -f {}'.format(os.path.join(self.binary_path, 'irecovery'), os.path.join('boot-{}'.format(self.device_id), 'ibot.img4')), shell=True)
                time.sleep(1)
            else:
                time.sleep(7)
                subprocess.run('{} -f {}'.format(os.path.join(self.binary_path, 'irecovery'), os.path.join('boot-{}'.format(self.device_id), 'iBSS.img4')), shell=True)
                time.sleep(7)
                subprocess.run('{} -f {}'.format(os.path.join(self.binary_path, 'irecovery'), os.path.join('boot-{}'.format(self.device_id), 'ibot.img4')), shell=True)
            if self.semi_tethered_option == '0':
                time.sleep(2)
                subprocess.run('{} -c fsboot'.format(os.path.join(self.binary_path, 'irecovery')), shell=True)
            if self.os_type == 'Darwin':
                subprocess.run('defaults write -g ignore-devices -bool false', shell=True)
                subprocess.run('defaults write com.apple.AMPDevicesAgent dontAutomaticallySyncIPods -bool false', shell=True)
                subprocess.run('killall Finder', shell=True)
        os.chdir(os.path.join(self.default_path, 'logs'))
        for log_file in os.listdir():
            if log_file.split('.')[-1] == 'log' and log_file == self.default_logfilename:
                if not 'SUCCESS_' in log_file:
                    os.rename(log_file, 'SUCCESS_{}'.format(log_file))
        os.chdir(self.default_path)
        try:
            shutil.rmtree('palera1n_work')
        except:
            pass
        try:
            shutil.rmtree('rdwork')
        except:
            pass
        print('Done!')
        print('''
The device should now boot to iOS
If this is your first time jailbreaking, open Tips app and then press Install
Otherwise, open Tips app and press Do All in the Tools section
If you have any issues, please join the Discord server and ask for help: https://dsc.gg/palera1n
Enjoy!''')
        # end


if __name__ == '__main__':
    palera1n()

sys.stdout == sys.__stdout__
sys.stderr == sys.__stderr__