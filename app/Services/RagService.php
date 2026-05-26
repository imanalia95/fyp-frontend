<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;

class RagService
{
    public function recommend($title, $description, $top_n = 3)
    {
        $response = Http::post(
            env('FASTAPI_URL') . '/api/recommend',
            [
                'title' => $title,
                'description' => $description,
                'top_n' => $top_n
            ]
        );

        return $response->json();
    }
}