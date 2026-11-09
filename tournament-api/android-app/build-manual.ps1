$ErrorActionPreference = 'Stop'
$project = $PSScriptRoot
$sdk = if ($env:ANDROID_HOME) { $env:ANDROID_HOME } else { Join-Path $env:LOCALAPPDATA 'Android\Sdk' }
$tools = Join-Path $sdk 'build-tools\36.0.0'
$sdkAndroidJar = Join-Path $sdk 'platforms\android-36\android.jar'
$javaHome = if ($env:JAVA_HOME) { $env:JAVA_HOME } else { 'C:\Program Files\Java\jdk-26.0.1' }
$javaBin = Join-Path $javaHome 'bin'
$build = Join-Path $project 'build-manual'
$res = Join-Path $project 'app\src\main\res'
$manifest = Join-Path $project 'app\src\main\AndroidManifest.xml'

foreach ($required in @($sdkAndroidJar, (Join-Path $tools 'aapt2.exe'), (Join-Path $tools 'd8.bat'), (Join-Path $javaBin 'javac.exe'))) {
    if (-not (Test-Path -LiteralPath $required)) { throw "Ferramenta Android ausente: $required" }
}

New-Item -ItemType Directory -Force -Path $build, (Join-Path $build 'generated'), (Join-Path $build 'classes'), (Join-Path $build 'dex') | Out-Null
$androidJar = Join-Path $build 'android.jar'
if (-not (Test-Path -LiteralPath $androidJar)) { Copy-Item -LiteralPath $sdkAndroidJar -Destination $androidJar }

& (Join-Path $tools 'aapt2.exe') compile --dir $res -o (Join-Path $build 'resources.zip')
if ($LASTEXITCODE -ne 0) { throw 'Falha ao compilar recursos.' }

& (Join-Path $tools 'aapt2.exe') link -o (Join-Path $build 'unsigned.apk') --manifest $manifest -I $androidJar --java (Join-Path $build 'generated') --min-sdk-version 24 --target-sdk-version 35 --version-code 1 --version-name 1.0.0 (Join-Path $build 'resources.zip')
if ($LASTEXITCODE -ne 0) { throw 'Falha ao montar APK.' }

$sources = @(Get-ChildItem (Join-Path $project 'app\src\main\java') -Recurse -Filter '*.java' | ForEach-Object FullName)
$sources += @(Get-ChildItem (Join-Path $build 'generated') -Recurse -Filter '*.java' | ForEach-Object FullName)
& (Join-Path $javaBin 'javac.exe') -source 8 -target 8 -Xlint:-options -classpath $androidJar -d (Join-Path $build 'classes') $sources
if ($LASTEXITCODE -ne 0) { throw 'Falha ao compilar o aplicativo.' }

& (Join-Path $javaBin 'jar.exe') cf (Join-Path $build 'classes.jar') -C (Join-Path $build 'classes') .
if ($LASTEXITCODE -ne 0) { throw 'Falha ao empacotar classes.' }

& (Join-Path $tools 'd8.bat') --lib $androidJar --output (Join-Path $build 'dex') (Join-Path $build 'classes.jar')
if ($LASTEXITCODE -ne 0) { throw 'Falha ao gerar código Android.' }

& (Join-Path $javaBin 'jar.exe') uf (Join-Path $build 'unsigned.apk') -C (Join-Path $build 'dex') classes.dex
if ($LASTEXITCODE -ne 0) { throw 'Falha ao adicionar código ao APK.' }

& (Join-Path $tools 'zipalign.exe') -f 4 (Join-Path $build 'unsigned.apk') (Join-Path $build 'aligned.apk')
if ($LASTEXITCODE -ne 0) { throw 'Falha ao alinhar APK.' }

$keystore = Join-Path $build 'debug.keystore'
if (-not (Test-Path -LiteralPath $keystore)) {
    & (Join-Path $javaBin 'keytool.exe') -genkeypair -keystore $keystore -storepass android -keypass android -alias androiddebugkey -dname 'CN=Android Debug,O=Android,C=US' -keyalg RSA -keysize 2048 -validity 10000
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao criar assinatura de teste.' }
}

$apk = Join-Path $project 'Racha-Android-debug.apk'
& (Join-Path $tools 'apksigner.bat') sign --ks $keystore --ks-pass pass:android --key-pass pass:android --ks-key-alias androiddebugkey --out $apk (Join-Path $build 'aligned.apk')
if ($LASTEXITCODE -ne 0) { throw 'Falha ao assinar APK.' }
& (Join-Path $tools 'apksigner.bat') verify --verbose $apk
if ($LASTEXITCODE -ne 0) { throw 'Falha ao verificar APK.' }
Write-Host "APK de teste: $apk"
