<?php
// ==========================================
// PHP 代码：查找最新图片的 URL
// ==========================================

// 定义图片根目录 (必须与 last.py 中的 SAVE_DIR 匹配)
$baseDir = './himawari'; // 保持不变，相对于 index.php 的路径
$latestImagePath = '';

// 1. 查找最新的日期文件夹 (格式: YYYYMMDD)
$dateFolders = [];
if (is_dir($baseDir)) {
    // 遍历 himawari 目录下的所有内容
    $items = scandir($baseDir, SCANDIR_SORT_DESCENDING); // 倒序扫描，最新的日期在前面

    foreach ($items as $item) {
        // 检查是否是文件夹，并且名称符合 YYYYMMDD 格式 (8位数字)
        if (is_dir($baseDir . '/' . $item) && preg_match('/^\d{8}$/', $item)) {
            // 找到最新的日期文件夹，通常是第一个
            $latestDateFolder = $item;
            break;
        }
    }
}

// 2. 在最新的日期文件夹中查找最新的 JPG 文件
if (isset($latestDateFolder)) {
    $targetDir = $baseDir . '/' . $latestDateFolder;
    $latestFile = '';
    $latestTimestamp = 0;

    // 遍历该日期文件夹下的所有文件
    $files = scandir($targetDir, SCANDIR_SORT_DESCENDING); // 倒序扫描，最新的文件在前面
    
    foreach ($files as $file) {
        // 确保文件以 .jpg 结尾且不是 . 或 ..
        if (pathinfo($file, PATHINFO_EXTENSION) === 'jpg') {
            // 由于文件命名就是时间戳，倒序扫描到的第一个 JPG 文件就是最新的
            $latestFile = $file;
            break;
        }
    }

    // 3. 构建完整的最新图片路径
    if ($latestFile) {
        $latestImagePath = $targetDir . '/' . $latestFile;
    }
}

// 4. 添加时间戳参数，确保浏览器不会缓存旧图片
// 如果找到了图片，就用它的路径；如果没找到，就用空字符串
$imageSrc = $latestImagePath ? $latestImagePath . '?t=' . time() : '';

// 备注: 删除了对 './himawari/last.jpg' 的判断和引用。
?>
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>Himawari-8 Earth View</title>
    <meta http-equiv="refresh" content="900">
    <style>
        /* 确保 body 覆盖整个视口，无边距 */
        body {
            background-color: black; /* 纯黑背景 */
            margin: 0;
            padding: 0;
            overflow: hidden; /* 防止出现滚动条 */
            
            /* 使用 Flexbox 确保图片在视口中居中 */
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh; /* 确保 body 占满整个视口高度 */
            width: 100vw;  /* 确保 body 占满整个视口宽度 */
        }
        
        /* 图片自动缩放以适应屏幕 */
        img {
            max-width: 100%;  /* 图片最大宽度不超过视口宽度 */
            max-height: 100%; /* 图片最大高度不超过视口高度 */
            height: auto;     /* 保持图片纵横比 */
            width: auto;      /* 保持图片纵横比 */
            
            /* 确保图片在缩放时保持纵横比，并完全包含在容器内 */
            object-fit: contain;
        }
    </style>
</head>
<body>
    <?php if ($imageSrc): ?>
        <img src="<?php echo $imageSrc; ?>" alt="Himawari 8 Full Disk Image">
    <?php endif; ?>
</body>
</html>
