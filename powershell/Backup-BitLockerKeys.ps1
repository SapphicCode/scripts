$vaultAddr = ""
$vaultMount = ""
$vaultPrefix = "bitlocker/"
$vaultToken = ""

$recoveryKeys = Get-BitLockerVolume |
    Where-Object VolumeStatus |
    Select-Object -ExpandProperty KeyProtector |
    Where-Object -Property KeyProtectorType -EQ RecoveryPassword

$recoveryKeys | ForEach-Object {
    $keyId = $_.KeyProtectorId
    $password = @{data = @{password = $_.RecoveryPassword}} | ConvertTo-Json
    Invoke-RestMethod -Uri "${vaultAddr}/v1/${vaultMount}/data/${vaultPrefix}/${keyId}" -Method Put -Headers @{"X-Vault-Token" = $vaultToken} -Body $password
}
