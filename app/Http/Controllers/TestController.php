<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Services\RagService;

class TestController extends Controller
{
    public function test()
    {
        $rag = new RagService();

        $result = $rag->recommend(
            "AI chatbot for education",
            "machine learning system for students",
            3
        );

        return response()->json($result);
    }
}