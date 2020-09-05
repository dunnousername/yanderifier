# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['yanderify.py', 'fomm\\demo.py'],
             pathex=['D:\\randomcode\\first-order-model-packed\\cuda1002\\yanderify'],
             binaries=[],
             datas=[('fomm\\config\\vox-256.yaml', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='yanderify',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='yanderify')
