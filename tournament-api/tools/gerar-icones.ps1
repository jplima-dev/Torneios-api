Add-Type -AssemblyName System.Drawing

$outputDir = Join-Path $PSScriptRoot '..\web\icons'
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

foreach ($size in @(192, 512)) {
    $bitmap = [System.Drawing.Bitmap]::new($size, $size)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    $graphics.Clear([System.Drawing.Color]::FromArgb(107, 30, 170))

    $orange = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(255, 173, 52))
    $purple = [System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(72, 23, 101), [float]($size * 0.027))
    $white = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::White)
    $shadow = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(109, 38, 92))

    $ball = [System.Drawing.RectangleF]::new([float]($size * 0.16), [float]($size * 0.16), [float]($size * 0.68), [float]($size * 0.68))
    $graphics.FillEllipse($orange, $ball)
    $graphics.DrawEllipse($purple, $ball)

    $clip = [System.Drawing.Drawing2D.GraphicsPath]::new()
    $clip.AddEllipse($ball)
    $graphics.SetClip($clip)
    $graphics.DrawLine($purple, [float]($size * 0.5), [float]($size * 0.1), [float]($size * 0.5), [float]($size * 0.9))
    $graphics.DrawLine($purple, [float]($size * 0.1), [float]($size * 0.5), [float]($size * 0.9), [float]($size * 0.5))
    $graphics.DrawEllipse($purple, [float]($size * -0.12), [float]($size * 0.16), [float]($size * 0.68), [float]($size * 0.68))
    $graphics.DrawEllipse($purple, [float]($size * 0.44), [float]($size * 0.16), [float]($size * 0.68), [float]($size * 0.68))
    $graphics.ResetClip()

    $font = [System.Drawing.Font]::new('Impact', [float]($size * 0.31), [System.Drawing.FontStyle]::Regular, [System.Drawing.GraphicsUnit]::Pixel)
    $alignment = [System.Drawing.StringFormat]::new()
    $alignment.Alignment = [System.Drawing.StringAlignment]::Center
    $alignment.LineAlignment = [System.Drawing.StringAlignment]::Center
    $bounds = [System.Drawing.RectangleF]::new(0, [float]($size * 0.31), [float]$size, [float]($size * 0.38))
    $offset = [System.Drawing.RectangleF]::new([float]($size * 0.013), [float]($size * 0.323), [float]$size, [float]($size * 0.38))
    $graphics.DrawString('R!', $font, $shadow, $offset, $alignment)
    $graphics.DrawString('R!', $font, $white, $bounds, $alignment)

    $path = Join-Path $outputDir "icon-$size.png"
    $bitmap.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $alignment.Dispose(); $font.Dispose(); $clip.Dispose()
    $shadow.Dispose(); $white.Dispose(); $purple.Dispose(); $orange.Dispose()
    $graphics.Dispose(); $bitmap.Dispose()
}
