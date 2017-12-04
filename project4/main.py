import numpy as np
import random
from PIL import Image
import tensorflow as tf
from groupmembers import print_group_members
from utilities import Utilities

def main():
	print_group_members()

	feature_for_classification = 'Eyeglasses'
	data_file_path = './data/img_align_celeba/'

	## read label file
	label_file_name = './data/list_attr_celeba.txt'
	features = np.genfromtxt(label_file_name, skip_header=1, max_rows=1, dtype='str')
	# print(len(features))
	# bad method but couldn't find any alternative
	feature_col_index = np.where(features == feature_for_classification)[0][0]
	print('Eyeglass column index: ', feature_col_index)
	
	label = np.genfromtxt(label_file_name, dtype= 'str',skip_header=2, usecols=(0, feature_col_index))
	dataset_count = len(label)
	training_count = int(0.8 * dataset_count)
	test_count = int(0.2*dataset_count)
	# python's random module isn’t made to deal with numpy arrays
	# since it’s not exactly the same as nested python lists
	np.random.shuffle(label)
	image_file_names = label[:, 0]
	predicted_output = label[:, 1]
	b = predicted_output.astype(np.int).clip(min=0)
	one_hot_outputs = np.eye(2)[b]
	# print(image_file_names)

	celeba_train_img_file_names = image_file_names[0:training_count]
	celeba_test_img_file_names = image_file_names[training_count+1:dataset_count]
	# print('train image count: ', len(celeba_train_img_file_names))
	# print('test image count: ', len(celeba_test_img_file_names))

	celeba_train_labels = one_hot_outputs[0:training_count]
	celeba_test_labels = one_hot_outputs[training_count:dataset_count]
	print('Num train labels: ', len(celeba_train_labels))
	print('Num test labels: ', len(celeba_test_labels))

	utilities = Utilities(data_file_path)
	celeba_train_images = utilities.load_images(training_count,celeba_train_img_file_names)
	celeba_test_images = utilities.load_images(test_count, celeba_test_img_file_names)

	print(len(celeba_train_images))

	train_cnn(utilities, celeba_train_images, celeba_train_labels,celeba_test_images,celeba_test_labels)


def train_cnn(utility_obj, training_data, training_label,celeba_test_images,celeba_test_labels):
	W_conv1 = utility_obj.weight_variable([5, 5, 1, 32])
	b_conv1 = utility_obj.bias_variable([32])
	x_image = tf.reshape(utility_obj.x_input, [-1, 28, 28, 1])
	h_conv1 = tf.nn.relu(utility_obj.conv2d(x_image, W_conv1) + b_conv1)
	h_pool1 = utility_obj.max_pool_2x2(h_conv1)

	# second layer in convolutional neural network
	W_conv2 = utility_obj.weight_variable([5, 5, 32, 64])
	b_conv2 = utility_obj.bias_variable([64])

	h_conv2 = tf.nn.relu(utility_obj.conv2d(h_pool1, W_conv2) + b_conv2)
	h_pool2 = utility_obj.max_pool_2x2(h_conv2)

	W_fc1 = utility_obj.weight_variable([7 * 7 * 64, 1024])
	b_fc1 = utility_obj.bias_variable([1024])

	h_pool2_flat = tf.reshape(h_pool2, [-1, 7 * 7 * 64])
	h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

	# drop random neurons to avoid overfitting
	
	h_fc1_drop = tf.nn.dropout(h_fc1, utility_obj.keep_prob)

	# we now perform the prediction using the basic logistic approach to compute the softmax
	# and then evaluating the output
	W_fc2 = utility_obj.weight_variable([1024, 2])
	b_fc2 = utility_obj.bias_variable([2])

	y_conv = tf.matmul(h_fc1_drop, W_fc2) + b_fc2

	cnn_accuracy, cnn_sess = utility_obj.compute_model_training(y_conv, training_data, training_label)

	test_batch_size = 1000
	test_data_size = len(celeba_test_labels)
	testing_batch_iterations = test_data_size // test_batch_size
	test_accuracy = 0.0
	
	for i in range(testing_batch_iterations):
		test_images_batch = celeba_test_images[i*test_batch_size : min((i+1)*test_batch_size, test_data_size)]
		target_labels_batch = celeba_test_labels[i*test_batch_size : min((i+1)*test_batch_size, test_data_size)]
		batch_test_accuracy = cnn_sess.run(cnn_accuracy,feed_dict={utility_obj.x_input: test_images_batch,
		utility_obj.y_labels: target_labels_batch, utility_obj.keep_prob: 1.0})
		test_accuracy = test_accuracy+batch_test_accuracy
		print('Testing batch = ',i,' Accuracy = ', batch_test_accuracy)
	print('Test data Accuracy = ', test_accuracy/testing_batch_iterations)	

	cnn_sess.close()

if __name__ == '__main__':
	main()