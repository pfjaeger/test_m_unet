import tensorflow as tf
import numpy as np
import logging


def _get_loss(logits, y, n_classes, loss_name, dim=2, class_weights=None):
	"""
	Constructs the cost function, either cross_entropy, weighted cross_entropy or dice_coefficient.
	Optional arguments are:
	class_weights: weights for the different classes in case of multi-class imbalance
	regularizer: power of the L2 regularizers added to the loss function
	"""
	if loss_name == 'cross_entropy':
		flat_logits = tf.reshape(logits, [-1, n_classes])
		flat_labels = tf.reshape(y, [-1, n_classes])
		if class_weights is not None:
			weight_map = tf.reduce_sum(tf.multiply(flat_labels, class_weights), axis=1)
			loss_map = tf.nn.softmax_cross_entropy_with_logits(logits=flat_logits, labels=flat_labels)
			loss = tf.reduce_mean(tf.multiply(loss_map, weight_map))

		else:
			loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=flat_logits, labels=flat_labels))
	elif loss_name == 'dice_coefficient':
		loss= 1. - tf.reduce_mean(get_dice_per_class(logits, y, dim))

	return loss


def _get_optimizer(loss, learning_rate):
	update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
	print 'CHECK UPDATE OPS:', update_ops
	if update_ops:
		with tf.control_dependencies(update_ops):
			optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(loss)
	else:
		optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(loss)
	return optimizer


def get_batch_dice_per_class(logits, y, dim=2): #doe not need for 3d anymore

	eps = tf.constant(float(1e-6))
	axes = tuple(range(dim - 2, dim + 1)) # batch as pseudo volume in 2D
	prediction = tf.nn.softmax(logits)
	intersection = tf.reduce_sum(prediction * y, axis=axes)
	union = eps + tf.reduce_sum(prediction, axis=axes) + tf.reduce_sum(y, axis=axes)
	dice_per_class = tf.constant(2.) * intersection / union
	return dice_per_class


def get_dice_per_class(logits, y, dim=3):

	eps = tf.constant(float(1e-6))
	axes = tuple(range(dim - 2, dim + 1)) # batch as pseudo volume in 2D
	prediction = tf.nn.softmax(logits)
	intersection = tf.reduce_sum(prediction * y, axis=axes)
	union = eps + tf.reduce_sum(prediction, axis=axes) + tf.reduce_sum(y, axis=axes)
	dice_per_class = tf.reduce_mean(tf.constant(2.) * intersection / union, axis=0)
	return dice_per_class

def get_slicewise_dice_per_class(logits, y, dim=2):

	eps = tf.constant(float(1e-6))
	axes = tuple(range(0, 1 + dim))
	prediction = tf.nn.softmax(logits)
	intersection = tf.reduce_sum(prediction * y, axis=axes)
	union = eps + tf.reduce_sum(prediction, axis=(1, 2)) + tf.reduce_sum(y, axis=axes)
	dice_per_class = tf.reduce_mean(tf.constant(2.) * intersection / union, axis=0)
	return dice_per_class


def numpy_dice_per_class(prediction, y):

	eps = 1e-4
	spatial_axes = tuple(range(1, len(y.shape) - 1))
	intersection = np.sum(prediction * y, axis=spatial_axes)
	union = eps + np.sum(prediction, axis=spatial_axes) + np.sum(y, axis=spatial_axes)
	dice_per_class = np.mean(2 * intersection / union, axis=0)
	return dice_per_class


def numpy_volume_dice_per_class(prediction, y):

	eps = 1e-4
	axes = tuple(range(0, len(y.shape) - 1))
	intersection = np.sum(prediction * y, axis=axes)
	union = eps + np.sum(prediction, axis=axes) + np.sum(y, axis=axes)
	dice_per_class = 2 * intersection / union
	return dice_per_class


def get_class_weights(seg, margin=0.1):
	"""
	get class weight values for a vector of pixels with sh....
	return weight vect...
	"""
	spatial_axes = tuple(range(1, len(seg.shape)-1))
	class_counts = np.sum(seg, axis=spatial_axes)
	spatial_counts = np.prod(np.array([seg.shape[ix] for ix in spatial_axes]))
	class_weights = 1 - (class_counts / float(spatial_counts)) + margin		 ###types???
	class_weights_flat = np.repeat(class_weights, seg.shape[1] ** len(spatial_axes), axis=0)
	return class_weights_flat


def get_one_hot_prediction(pred, n_classes):
	"""
	transform a softmax prediction to a one-hot prediction of the same shape
	"""
	print pred.shape, "CHECK SHAPE"
	pred_one_hot = np.zeros(list(pred.shape) + [n_classes]).astype('int32')
	print pred_one_hot.shape, "CHECK SHAPE"
	for cl in range(n_classes):
		pred_one_hot[..., cl][pred == cl] = 1
	return pred_one_hot


def get_logger(cf):


	logger = logging.getLogger('UNet_training')
	log_file = cf.exp_dir + '/exec.log'
	print('Logging to {}'.format(log_file))
	hdlr = logging.FileHandler(log_file)
	logger.addHandler(hdlr)
	# logger.addHandler(logging.StreamHandler())
	logger.setLevel(logging.DEBUG)
	logger.info('Created Exp. Dir: {}.'.format(cf.exp_dir))
	return logger
