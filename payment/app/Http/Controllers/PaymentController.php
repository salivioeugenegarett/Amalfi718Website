<?php

$curl = curl_init();

curl_setopt_array($curl, [
  CURLOPT_URL => "https://api.paymongo.com/v1/links",
  CURLOPT_RETURNTRANSFER => true,
  CURLOPT_ENCODING => "",
  CURLOPT_MAXREDIRS => 10,
  CURLOPT_TIMEOUT => 30,
  CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
  CURLOPT_CUSTOMREQUEST => "POST",
  CURLOPT_POSTFIELDS => json_encode([
    'data' => [
        'attributes' => [
                'amount' => 129900,
                'description' => 'Standard Room',
                'remarks' => 'Thankyou for Booking!'
        ]
    ]
  ]),
  CURLOPT_HTTPHEADER => [
    "accept: application/json",
    "authorization: Basic c2tfdGVzdF9uUnVobmFFMk1uZFYyNzhrbXJzaExGdEY6",
    "content-type: application/json"
  ],
]);

$response = curl_exec($curl);
$err = curl_error($curl);

curl_close($curl);

if ($err) {
  echo "cURL Error #:" . $err;
} else {
    $decoded = json_decode($response, true);

    if (isset($decoded['data']['attributed']['checkout_url'])) {
        $checkoutURL = $decoded['data']['attributes']['checkout_url'];

        header("Location:  $checkoutUrl");
        exit();

    } else { 
        echo "Failed to get checkout URL from response: ";
        
    }
}
?>