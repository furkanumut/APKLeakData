#jadx and apktool apk decompile with class

import os
import shutil

class ApkDecompiler:
    def __init__(self, apkpath, decompiler, decompilepath):
        self.apkpath = apkpath
        self.decompilepath = decompilepath
        self.decompiler = decompiler
        if self.decompiler == 'apktool':
            self.decompile_status = self.apktool_decompile()
        elif self.decompiler == 'jadx':
            self.decompile_status = self.jadx_decompile()
        
    def apktool_decompile(self):
        return os.system("apktool d -o '%s' '%s' >/dev/null" % (self.decompilepath, self.apkpath))
    
    def jadx_decompile(self):
        return os.system("jadx -d '%s' '%s' >/dev/null" % (self.decompilepath, self.apkpath))

    def clean_decompile(decompilepath):
        return shutil.rmtree(decompilepath)