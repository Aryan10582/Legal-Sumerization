param([Parameter(Mandatory=$true)][string]$InputDocx,[Parameter(Mandatory=$true)][string]$OutputPdf)
$ErrorActionPreference='Stop'
$inputResolved=(Resolve-Path -LiteralPath $InputDocx).Path
$pdfResolved=[System.IO.Path]::GetFullPath($OutputPdf)
$word=$null
$document=$null
try {
    $word=New-Object -ComObject Word.Application
    $word.Visible=$false
    $word.DisplayAlerts=0
    $document=$word.Documents.Open($inputResolved,$false,$true)
    $document.ExportAsFixedFormat($pdfResolved,17)
    Write-Output "Exported $pdfResolved; pages=$($document.ComputeStatistics(2))"
} finally {
    if($null -ne $document){$document.Close(0)}
    if($null -ne $word){$word.Quit()}
}
