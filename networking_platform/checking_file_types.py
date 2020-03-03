import flask, sys
from flask import Flask, flash

def verify_valid_image(photo_file):
	# Checking the file type of images after the upload button is clicked on the site.
	# This function will need to be called when the user uploads their profile picture,
	# and each photo uploaded to the carousel.

	bool_is_image_valid = photo_file.lower().endswith(('.png', '.jpg', '.jpeg'))

	return bool_is_image_valid

def verify_PDF_image(file):
	# Checking the file type of the resume and cover letter uploaded. These files
	# need to be of type PDF and this function will need to be called anytime
	# the user clicks that upload button on their resume and cover letter 
	# portfolio tabs. 

	bool_is_file_valid = file.lower().endswith(('.pdf'))

	return bool_is_file_valid