function Backup-BitLockerKeys {
    [CmdletBinding()]
    Param(
        [Parameter(Mandatory)]
        [string] $VaultAddress,

        [Parameter(Mandatory)]
        [string] $VaultMount,

        [Parameter()]
        [string] $VaultPrefix,

        [Parameter(Mandatory)]
        [string] $VaultToken
    )

    $recoveryKeys = Get-BitLockerVolume |
    Where-Object VolumeStatus |
    Select-Object -ExpandProperty KeyProtector |
    Where-Object -Property KeyProtectorType -EQ RecoveryPassword

    $recoveryKeys | ForEach-Object {
        $keyId = $_.KeyProtectorId
        $password = @{data = @{password = $_.RecoveryPassword } } | ConvertTo-Json
        Invoke-RestMethod -Uri "${VaultAddress}/v1/${VaultMount}/data/${VaultPrefix}/${keyId}" -Method Put -Headers @{"X-Vault-Token" = $VaultToken } -Body $password
    }
}