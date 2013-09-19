function drawDatapath() {
	var canvas = $('#workspace').get(0).getContext('2d');
	var image = new Image();
	image.src = '/img/pipeline.png';
	image.onload = function() {
		canvas.drawImage(image, 0, 10);
	}
}
