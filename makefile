IMAGE_NAME = pices-project
TAG = latest

build:
	docker build -t $(IMAGE_NAME):$(TAG) .

run:
	docker run -it --rm \
		-v $(CURDIR):/app \
		$(IMAGE_NAME):$(TAG)



