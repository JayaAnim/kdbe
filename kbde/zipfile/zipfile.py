import zipfile, os


class ZipFile(zipfile.ZipFile):
    
    def _extract_member(self, member, targetpath, pwd):
        if not isinstance(member, zipfile.ZipInfo):
            member = self.getinfo(member)

        targetpath = super()._extract_member(member, targetpath, pwd)

        attr = member.external_attr >> 16

        if attr != 0:
            os.chmod(targetpath, attr)

        return targetpath
