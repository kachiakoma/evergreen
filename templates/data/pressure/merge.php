<?php
$path = getcwd()."/*.json";
$master = glob(getcwd()."/0.json");
$files = glob($path);
echo "<pre>";

if($files && $files != $master ){
	$combine=array();
	foreach($files as $file)
	{
		$string = file_get_contents($file);
		$json_current = json_decode($string, true);
		foreach($json_current as $json)
		{
		$current=array();
		array_push($current,$json[0],$json[1]);
		array_push($combine,$current);
		}
	}
	// Convert to combined json and write the file
	$file_combined=getcwd()."/cleaned/0.json";
	$combined_json=json_encode($combine);
	$result=file_put_contents($file_combined,$combined_json);
	if($result)
	{
		echo "the combined file is here $file_combined";
	}
	else
	{
		echo "Error Writing Combined Json File";
	}
	// Delete all .json files from merge folder
	$path=getcwd()."/*.json";
	$files = glob($path);
	$destination=getcwd()."/0.json";
	array_map('unlink', $files);
	// Copy master .json back into merge folder
	copy($file_combined, $destination);
}
else
{
	echo "nothing to do";
}
?>
