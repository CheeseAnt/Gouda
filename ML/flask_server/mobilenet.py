import sys
sys.path.append('/home/anton/Documents/models/research/slim/')

import tensorflow as tf
from datasets import imagenet
from nets.mobilenet import mobilenet_v2

class MobileNet:
    def __init__(self, checkpoint='../mobilenet_v2_1.0_224.ckpt'):
        self.checkpoint = checkpoint

        tf.reset_default_graph()

        self.file_in = tf.placeholder(tf.string, ())
        image = tf.image.decode_jpeg(tf.read_file(self.file_in))

        inputs = tf.expand_dims(image, 0)
        inputs = (tf.cast(inputs, tf.float32) / 128) - 1
        inputs.set_shape((None, None, None, 3))
        inputs = tf.image.resize_images(inputs, (224, 224))

        with tf.contrib.slim.arg_scope(mobilenet_v2.training_scope(is_training=False)):
          logits, self.endpoints = mobilenet_v2.mobilenet(inputs)
          
        # Restore using exponential moving average since it produces (1.5-2%) higher 
        # accuracy
        ema = tf.train.ExponentialMovingAverage(0.999)
        vars = ema.variables_to_restore()

        saver = tf.train.Saver(vars)

        self.label_map = imagenet.create_readable_names_for_imagenet_labels()  
        
        self.sess = tf.Session()
        saver.restore(self.sess, self.checkpoint)

    def infer(self, filename):
        x = self.endpoints['Predictions'].eval(feed_dict={self.file_in: filename},
            session=self.sess)

        print("Top 1 prediction: ", x.argmax(), self.label_map[x.argmax()], x.max())

