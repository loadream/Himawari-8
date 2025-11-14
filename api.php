<?php
// ==========================================
// PHP API 脚本：查找最新图片的 URL 并输出 JSON (无查询参数)
// ==========================================

// 设置内容类型为 JSON，确保客户端正确解析
header('Content-Type: application/json');

// ******** 定义您的完整域名 ********
$baseUrl = 'https://earth.loadream.com/';
// **********************************

// 定义图片根目录 (必须与 last.py 中的 SAVE_DIR 匹配)
$baseDir = './himawari'; // 相对于 PHP 脚本的路径
$latestImagePath = '';
$imageFound = false;

// 1. 查找最新的日期文件夹 (格式: YYYYMMDD)
$latestDateFolder = null;
if (is_dir($baseDir)) {
    // 倒序扫描，最新的日期在前面
    $items = scandir($baseDir, SCANDIR_SORT_DESCENDING); 

    foreach ($items as $item) {
        // 检查是否是文件夹，并且名称符合 YYYYMMDD 格式 (8位数字)
        if (is_dir($baseDir . '/' . $item) && preg_match('/^\d{8}$/', $item)) {
            $latestDateFolder = $item;
            break; // 找到最新的就退出循环
        }
    }
}

// 2. 在最新的日期文件夹中查找最新的 JPG 文件
if ($latestDateFolder) {
    $targetDir = $baseDir . '/' . $latestDateFolder;
    $latestFile = '';
    
    // 倒序扫描，最新的文件在前面
    $files = scandir($targetDir, SCANDIR_SORT_DESCENDING); 
    
    foreach ($files as $file) {
        // 确保文件以 .jpg 结尾且不是 . 或 ..
        if (pathinfo($file, PATHINFO_EXTENSION) === 'jpg') {
            $latestFile = $file;
            break; // 找到最新的就退出循环
        }
    }

    // 3. 构建完整的最新图片路径和 URL
    if ($latestFile) {
        // 构建服务器上的相对路径
        $latestImagePath = $targetDir . '/' . $latestFile;
        $imageFound = true;
    }
}

// 4. 构建响应数据
$response = [
    'success' => $imageFound,
    'timestamp' => time(), // API 请求的时间戳
    'latest_url' => '',
    'filename' => $latestFile ?? null
];

if ($imageFound) {
    // 构建完整的 URL
    // 移除路径前面的 './'，使其成为一个有效的相对 URL
    $cleanPath = ltrim($latestImagePath, './'); 
    
    // 拼接 Base URL 和相对路径，不加 ?t= 参数
    $fullUrl = $baseUrl . $cleanPath;
    
    $response['latest_url'] = $fullUrl;
} else {
    // 如果没有找到图片
    http_response_code(404); // 返回 404 状态码
    $response['message'] = 'Latest image not found in the expected directory structure.';
}

// 5. 输出 JSON
echo json_encode($response, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
?>
