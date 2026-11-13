import argostranslate.package
argostranslate.package.update_package_index()
models = argostranslate.package.get_available_packages()
model = next((p for p in models if p.from_code=='ko' and p.to_code=='en'), None)
if not model:
    raise SystemExit('ko-en model unavailable')
argostranslate.package.install_from_path(model.download())
print('ko-en translation model installed')
