# Export all formats from GameRes and ArcFormats into JSON
[System.Reflection.Assembly]::LoadFrom((Resolve-Path "vendor\GARbro\bin\Release\GameRes.dll")) | Out-Null
[System.Reflection.Assembly]::LoadFrom((Resolve-Path "vendor\GARbro\bin\Release\ArcFormats.dll")) | Out-Null

$catalog = [GameRes.FormatCatalog]::Instance
$formats = @()

foreach ($arc in $catalog.ArcFormats) {
    $canCreate = $false
    try {
        $method = $arc.GetType().GetMethod("Create", [System.Reflection.BindingFlags]"Public,Instance,DeclaredOnly")
        if ($null -ne $method) { $canCreate = $true }
    } catch {}

    $formats += [PSCustomObject]@{
        Tag = $arc.Tag
        Kind = "archive"
        Description = $arc.Description
        Extensions = ($arc.Extensions -join ", ")
        Signatures = ($arc.Signatures | ForEach-Object { "0x{0:X8}" -f $_ }) -join ", "
        CanExtract = $true
        CanConvert = $false
        CanCreate = $canCreate
        ClassName = $arc.GetType().FullName
    }
}

foreach ($img in $catalog.ImageFormats) {
    $canWrite = $false
    try {
        $method = $img.GetType().GetMethod("Write", [System.Reflection.BindingFlags]"Public,Instance,DeclaredOnly")
        if ($null -ne $method) { $canWrite = $true }
    } catch {}

    $formats += [PSCustomObject]@{
        Tag = $img.Tag
        Kind = "image"
        Description = $img.Description
        Extensions = ($img.Extensions -join ", ")
        Signatures = ($img.Signatures | ForEach-Object { "0x{0:X8}" -f $_ }) -join ", "
        CanExtract = $false
        CanConvert = $true
        CanCreate = $canWrite
        ClassName = $img.GetType().FullName
    }
}

foreach ($aud in $catalog.AudioFormats) {
    $canWrite = $false
    try {
        $method = $aud.GetType().GetMethod("Write", [System.Reflection.BindingFlags]"Public,Instance,DeclaredOnly")
        if ($null -ne $method) { $canWrite = $true }
    } catch {}

    $formats += [PSCustomObject]@{
        Tag = $aud.Tag
        Kind = "audio"
        Description = $aud.Description
        Extensions = ($aud.Extensions -join ", ")
        Signatures = ($aud.Signatures | ForEach-Object { "0x{0:X8}" -f $_ }) -join ", "
        CanExtract = $false
        CanConvert = $true
        CanCreate = $canWrite
        ClassName = $aud.GetType().FullName
    }
}

foreach ($scr in $catalog.ScriptFormats) {
    $formats += [PSCustomObject]@{
        Tag = $scr.Tag
        Kind = "script"
        Description = $scr.Description
        Extensions = ($scr.Extensions -join ", ")
        Signatures = ($scr.Signatures | ForEach-Object { "0x{0:X8}" -f $_ }) -join ", "
        CanExtract = $false
        CanConvert = $false
        CanCreate = $false
        ClassName = $scr.GetType().FullName
    }
}

$jsonPath = Join-Path $PSScriptRoot "formats_inventory.json"
$formats | ConvertTo-Json -Depth 5 | Set-Content -Path $jsonPath -Encoding UTF8
Write-Host "Exported $($formats.Count) formats to $jsonPath"
