<?php
session_start();
include_once '../init/vars.php';
require_once '../database/bucket_count.php';

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');


function handleApiCall(string $model, string $responseNumber, string $query) {
    global $protect;
    
    // $pairwise = $content['pairwise'];
    // $query = htmlspecialchars($content['query']);
    $query_message = ["role" => "user", "content" => $query];
    $_SESSION['conversation_' . $responseNumber][] = $query_message;

    if ($model == 'gpt-4o-mini') {
        $apiKey = $protect['api']['openai'];
        $url = 'https://api.openai.com/v1/chat/completions';
        $data = [
            'model' => $model,
            'messages' => $_SESSION['conversation_' . $responseNumber],
            'max_tokens' => 500
        ];
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'Authorization: Bearer ' . $apiKey,
            'Content-Type: application/json'
        ]);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        $apiResponse = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $decoded_response = json_decode($apiResponse, true);
        if ($apiResponse === false) {
            responseFailure(500, 'cURL Error: ' . curl_error($ch));
        } elseif ($httpCode >= 400) {
            // responseFailure(500, 'OpenAI API Error: ' . $decoded_response['error']['message']);
            $message = $decoded_response['error']['message'];
            curl_close($ch);
            return [
                'content' => "AI Error. Please report to the study administrator with the following: {'code': $httpCode, 'message': $message, 'model': $model}",
                "model" => $data['model']
            ]; 
        } else {
            $_SESSION['conversation_' . $responseNumber][] = $decoded_response['choices'][0]['message'];
            // $response['content'] = $decoded_response['choices'][0]['message']['content'];
            // $response['model'] = $data['model'];

            curl_close($ch);
            return [
                'content' => $decoded_response['choices'][0]['message']['content'], 
                "model" => $data['model']
            ];
        }
    } elseif ($model == 'claude-sonnet-4-5-20250929') {
        $apiKey = $protect['api']['anthropic'];
        $url = "https://api.anthropic.com/v1/messages";
        $data = [
            'model' => $model,
            'messages' => $_SESSION['conversation_' . $responseNumber],
            'max_tokens' => 500
        ];
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'x-api-key: ' . $apiKey,
            'anthropic-version: 2023-06-01',
            'content-type: application/json'
        ]);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        $apiResponse = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $decoded_response = json_decode($apiResponse, true);
        if ($apiResponse === false) {
            curl_close($ch);
            responseFailure(500, 'cURL Error: ' . curl_error($ch));
        } elseif ($httpCode >= 400) {
            // responseFailure(500, 'Anthropic API Error: ' . $decoded_response['error']['message']);
            $message = $decoded_response['error']['message'];
            curl_close($ch);
            return [
                'content' => "AI Error. Please report to the study administrator with the following: {'code': $httpCode, 'message': $message, 'model': $model}",
                "model" => $data['model']
            ]; 
        } else {
            $text_response = $decoded_response['content'][0]['text'];
            $_SESSION['conversation_' . $responseNumber][] = ["role" => "assistant", "content" => $text_response];
            // $response['content'] = $decoded_response;
            // $response['model'] = $data['model'];

            curl_close($ch);
            return [
                'content' => $text_response, 
                "model" => $data['model']
            ];
        }
    // } elseif (str_contains($model, 'meta-llama')) {
    } else {
        $data = [
            "model" => $model,
            "messages" => $_SESSION['conversation_' .$responseNumber],
            "max_tokens" => 500,
            // "temperature" => 0.7,
            // "top_p" => 0.7,
            // "top_k" => 50,
            // "repetition_penalty" => 1,
            // "stop" => ["<|eot_id|>","<|eom_id|>"],
            // "stream" => true
        ];
        // $data = [
        //     "model" => "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        //     "messages" => $_SESSION['conversation_' .$responseNumber],
        //     "max_tokens" => 500,
        //     // "temperature" => 0.7,
        //     // "top_p" => 0.7,
        //     // "top_k" => 50,
        //     // "repetition_penalty" => 1,
        //     // "stop" => ["<|eot_id|>","<|eom_id|>"],
        //     // "stream" => true
        // ];

        // if ($model == 'deepseek-ai/DeepSeek-V3') {
        //     $data['model'] = 'deepseek-ai/DeepSeek-V3';
        // }
            // } else {
        //     // $data['model'] = 'mistralai/Mistral-Small-24B-Instruct-2501';
        //     $data['model'] = 'deepseek-ai/DeepSeek-V3';
        // }
        $apiKey = $protect['api']['together'];
        $url = 'https://api.together.xyz/v1/chat/completions';
        $ch = curl_init($url);

        curl_setopt_array($ch, array(
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_ENCODING => '',
            CURLOPT_MAXREDIRS => 10,
            CURLOPT_TIMEOUT => 0,
            CURLOPT_FOLLOWLOCATION => true,
            CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
            CURLOPT_CUSTOMREQUEST => 'POST',
            CURLOPT_POSTFIELDS => json_encode($data),
            CURLOPT_HTTPHEADER => array(
                'Content-Type: application/json',
                'Authorization: Bearer ' . $apiKey
            ),
        ));
        $apiResponse = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $decoded_response = json_decode($apiResponse, true);
        if ($apiResponse === false) {
            curl_close($ch);
            responseFailure(500, 'cURL Error: ' . curl_error($ch));
        } elseif ($httpCode >= 400) {
            $message = $decoded_response['error']['message'];
            curl_close($ch);
            return [
                'content' => "AI Error. Please report to the study administrator with the following: {'code': $httpCode, 'message': null, 'model': $model}",
                "model" => $data['model']
            ]; 
        } else {
            $text_response = $decoded_response["choices"][0]['message']['content'];
            $_SESSION['conversation_' . $responseNumber][] = ["role" => "assistant", "content" => $text_response];
            //["role" => $decoded_response['choices'][0]['message']['role'], "content" => $decoded_response['choices'][0]['message']['content']];
            // $response['content'] = $decoded_response['choices'][0]['message']['content'];
            // $response['model'] = $data['model'];

            curl_close($ch);
            return [
                'content' => $text_response, 
                "model" => $data['model']
            ];
        }
    }
}

function fisherYatesShuffle($array) {
    for ($i = count($array) - 1; $i > 0; $i--) {
        $j = mt_rand(0, $i);
        $temp = $array[$i];
        $array[$i] = $array[$j];
        $array[$j] = $temp;
    }
    return $array;
}

if($_SERVER['REQUEST_METHOD'] == 'POST'){
    header('Content-Type: application/json');

    if($_SERVER['HTTP_X_CSRF_TOKEN'] != $_SESSION['csrf_token']){
        responseFailure(403, "Invalid CSRF Token");
    }

    $content = json_decode(file_get_contents('php://input'), true);
    if (!isset($content['pairwise']) || !isset($content['query'])){
        responseFailure(400, "Missing keys in body of POST request");
    }
    $pairwise = $content['pairwise'];
    $query = $content['query'];

    $wasPromptAdjusted = false; 
    if (mt_rand(0, 1) === 1) {
        $query .= " respond using bullet points";
        $wasPromptAdjusted = true;
    }

    $response = [
        'status' => 'success',
        'wasPromptAdjusted' => $wasPromptAdjusted
    ];

    // $models = [1, 2, 3, 4];
    $models = ['gpt-4o-mini', 'claude-sonnet-4-5-20250929', 'meta-llama/Llama-3.3-70B-Instruct-Turbo', 'deepseek-ai/DeepSeek-V3.1'];
    // $models = ['gpt-4o-mini', 'claude-sonnet-4-5-20250929'];
    // $models = ['claude-sonnet-4-5-20250929'];


    if (empty($_SESSION['conversation_1']) && empty($_SESSION['conversation_2'])) {
        $shuffledModels = fisherYatesShuffle($models); 
        // $models = ['gpt-4o-mini', 'claude-3-5-sonnet-20240620', 'meta-llama/Llama-3.3-70B-Instruct-Turbo', 'deepseek-ai/DeepSeek-V3'];
    
        $buckets = get_model_buckets($models);
        $response['buckets'] = $buckets;
    
        $filteredModels = [];
        foreach($shuffledModels as $model){
            if($buckets[$model] < 40){
                $filteredModels[] = $model;
            }
        }
            
        $selectModel1 = $shuffledModels[0];
        $selectModel2 = $shuffledModels[1];
    
        if (count($filteredModels) >= 2){
            $selectModel1 = $filteredModels[0];
            $selectModel2 = $filteredModels[1];
        } elseif (count($filteredModels) == 1){
            $selectModel1 = $filteredModels[0];
        } 
                            
        $_SESSION['selected_model_1'] = $selectModel1;
        $_SESSION['selected_model_2'] = $selectModel2;
    } else {
        $selectModel1 = $_SESSION['selected_model_1'];
        $selectModel2 = $_SESSION['selected_model_2'];
    }


    // $response['session1'] = $_SESSION['selected_model_1'];    
    // $response['session2'] = $_SESSION['selected_model_2'];
    // $response['convo'] = $_SESSION['con']
    // $response['filtered'] = $filteredModels;
    // $response['pairwise'] = $pairwise;
    
    if ($pairwise === true) {
        $model_1 = handleApiCall($selectModel1, "1", $query);
        $model_2 = handleApiCall($selectModel2, "2", $query);
        // $response['selectedmodel2'] = $model_2;

        $response['conversation'] = [$model_1, $model_2];
    } else {
        $model_1 = handleApiCall($selectModel1, "1", $query);
        $response['conversation'] = [$model_1];
    }
    
    // $response['conversation'] = [$model_1];
    
    // $response['extra'] = !isset($content['pairwise']);
    
    echo json_encode($response);
} 
