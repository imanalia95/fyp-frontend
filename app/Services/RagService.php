<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;

class RagService
{
    public function recommend($title, $description, $top_n = 3)
    {
        $response = Http::post(
            'https://lovely-abundance-production-2737.up.railway.app/api/recommend',
            [
                'title' => $title,
                'description' => $description,
                'top_n' => $top_n
            ]
        );

        return $response->json();
    }
}