#jadx and apktool apk decompile with class

import os
import shutil

class ApkDecompiler:
    def __init__(self, apk_path, decompiler, decompile_path):
        self.apk_path = apk_path
        self.decompile_path = decompile_path
        self.decompiler = decompiler
        if self.decompiler == 'apktool':
            self.decompile_status = self.apktool_decompile()
        elif self.decompiler == 'jadx':
            self.decompile_status = self.jadx_decompile()
        
    def apktool_decompile(self):
        return os.system("apktool d -o '%s' '%s' >/dev/null" % (self.decompile_path, self.apk_path))
    
    def jadx_decompile(self):
        return os.system("jadx -d '%s' '%s' >/dev/null" % (self.decompile_path, self.apk_path))

    def clean_decompile_path(decompile_path):
        return shutil.rmtree(decompile_path)