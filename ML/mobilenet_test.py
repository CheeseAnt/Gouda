import sys
sys.path.append('/home/anton/Documents/models/research/slim/')

import tensorflow as tf
from datasets import imagenet
from nets.mobilenet import mobilenet_v2

checkpoint = 'mobilenet_v2_1.0_224.ckpt'

tf.reset_default_graph()

file_in = tf.placeholder(tf.string, ())
image = tf.image.decode_jpeg(tf.read_file(file_in))

inputs = tf.expand_dims(image, 0)
inputs = (tf.cast(inputs, tf.float32) / 128) - 1
inputs.set_shape((None, None, None, 3))
inputs = tf.image.resize_images(inputs, (224, 224))

with tf.contrib.slim.arg_scope(mobilenet_v2.training_scope(is_training=False)):
  logits, endpoints = mobilenet_v2.mobilenet(inputs)
  
# Restore using exponential moving average since it produces (1.5-2%) higher 
# accuracy
ema = tf.train.ExponentialMovingAverage(0.999)
vars = ema.variables_to_restore()

saver = tf.train.Saver(vars)

with tf.Session() as sess:
  saver.restore(sess,  checkpoint)
  x = endpoints['Predictions'].eval(feed_dict={file_in: 'panda.jpg'})
label_map = imagenet.create_readable_names_for_imagenet_labels()  

print("Top 1 prediction: ", x.argmax(),label_map[x.argmax()], x.max())

