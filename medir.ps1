$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$build = Join-Path $root "build"
$data = Join-Path $root "dados"
$sizes = @(25000, 50000, 100000, 200000)
$java = "java"

function Invoke-Csv([string[]] $arguments) {
    $output = @(& $java @arguments 2>&1)
    if ($LASTEXITCODE -ne 0) { throw "Falha: java $($arguments -join ' ')" }
    $line = [string]$output[-1]
    if ($line -notmatch "^[^;]+;[0-9]+;") { throw "Saída inesperada: $line" }
    return $line
}

function Add-Row([string] $path, [string] $line) {
    [IO.File]::AppendAllText($path, $line + [Environment]::NewLine)
}

foreach ($n in $sizes) {
    & $java "-cp" $build "app.GeradorArquivo" $n (Join-Path $data "cres_$n.txt") "crescente"
    if ($LASTEXITCODE -ne 0) { throw "Falha ao gerar cres_$n.txt" }
    & $java "-cp" $build "app.GeradorArquivo" $n (Join-Path $data "bal_$n.txt") "balanceado"
    if ($LASTEXITCODE -ne 0) { throw "Falha ao gerar bal_$n.txt" }
}

$resultados = Join-Path $data "resultados.csv"
$contagens = Join-Path $data "contagens.csv"
[IO.File]::WriteAllText($resultados, "estrutura;n;montagem_ms;altura_tel;altura_nome;busca_tel_ms;busca_nome_ms;remocao_ms;achouTel;achouNome;removeu$([Environment]::NewLine)", [Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllText($contagens, "rotulo;n;comp_montagem;comp_busca_tel;altura_tel$([Environment]::NewLine)", [Text.UTF8Encoding]::new($false))

foreach ($n in $sizes) {
    1..3 | ForEach-Object {
        $line = Invoke-Csv @("-Xmx3g","-cp",$build,"app.Benchmark",(Join-Path $data "bal_$n.txt"),"arvore")
        Add-Row $resultados ($line -replace "^arvore;", "arvore_balanceada;")
    }
}
foreach ($n in $sizes) {
    1..3 | ForEach-Object {
        $line = Invoke-Csv @("-Xmx3g","-cp",$build,"app.Benchmark",(Join-Path $data "cres_$n.txt"),"avl")
        Add-Row $resultados ($line -replace "^avl;", "avl_crescente;")
    }
}
foreach ($n in $sizes) {
    1..3 | ForEach-Object {
        $line = Invoke-Csv @("-Xmx3g","-cp",$build,"app.Benchmark",(Join-Path $data "bal_$n.txt"),"avl")
        Add-Row $resultados ($line -replace "^avl;", "avl_balanceada;")
    }
}
foreach ($n in $sizes) {
    1..3 | ForEach-Object {
        Add-Row $resultados (Invoke-Csv @("-Xmx3g","-cp",$build,"app.Benchmark",(Join-Path $data "bal_$n.txt"),"lista_nao_ordenada"))
    }
}
foreach ($n in $sizes) {
    1..3 | ForEach-Object {
        $line = Invoke-Csv @("-Xmx3g","-cp",$build,"app.Benchmark",(Join-Path $data "cres_$n.txt"),"arvore")
        Add-Row $resultados ($line -replace "^arvore;", "arvore_degenerada;")
    }
}
foreach ($n in $sizes) {
    Add-Row $resultados (Invoke-Csv @("-Xmx3g","-cp",$build,"app.Benchmark",(Join-Path $data "bal_$n.txt"),"lista_ordenada"))
}

foreach ($n in $sizes) {
    Add-Row $contagens (Invoke-Csv @("-Xmx3g","-cp",$build,"app.ContagemOperacoes",(Join-Path $data "bal_$n.txt"),"arvore_balanceada"))
}
foreach ($n in $sizes) {
    Add-Row $contagens (Invoke-Csv @("-Xmx3g","-cp",$build,"app.ContagemOperacoes",(Join-Path $data "cres_$n.txt"),"avl_crescente","avl"))
}
foreach ($n in $sizes) {
    Add-Row $contagens (Invoke-Csv @("-Xmx3g","-cp",$build,"app.ContagemOperacoes",(Join-Path $data "cres_$n.txt"),"arvore_degenerada"))
}