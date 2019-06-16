import sys
sys.path.append('/home/pi/Documents/models/research/slim/')

import tensorflow as tf
from datasets import imagenet
from nets.mobilenet import mobilenet_v2

## Class to perform classification on an image saved in the local directory using MobileNet
class MobileNet:
    def __init__(self, checkpoint='../mobilenet_v2_1.0_224.ckpt'):
        # save the checkpoint
        self.checkpoint = checkpoint

        tf.reset_default_graph()

        # placeholder for the image input, need to decode the file
        self.file_in = tf.placeholder(tf.string, ())
        image = tf.image.decode_jpeg(tf.read_file(self.file_in))

        # expand for batch then cast to between -1 and 1
        inputs = tf.expand_dims(image, 0)
        inputs = (tf.cast(inputs, tf.float32) / 128) - 1
        # ensure that it only has three dimensions and resize to 224x224
        inputs.set_shape((None, None, None, 3))
        inputs = tf.image.resize_images(inputs, (224, 224))

        get the endpoints of the network
        with tf.contrib.slim.arg_scope(mobilenet_v2.training_scope(is_training=False)):
          _, self.endpoints = mobilenet_v2.mobilenet(inputs)
          
        # Restore using exponential moving average since it produces (1.5-2%) higher 
        # accuracy
        ema = tf.train.ExponentialMovingAverage(0.999)
        vars = ema.variables_to_restore()

        saver = tf.train.Saver(vars)

        # create the label map from imagenet, same thing
        self.label_map = imagenet.create_readable_names_for_imagenet_labels()  
        
        # create session and restore the checkpoint downloaded
        self.sess = tf.Session()
        saver.restore(self.sess, self.checkpoint)

    def infer(self, filename):
        # perform inference on the file provided, print the results and return them
        x = self.endpoints['Predictions'].eval(feed_dict={self.file_in: filename},
            session=self.sess)

        print("Top 1 prediction: ", x.argmax(), self.label_map[x.argmax()], x.max())

        return self.label_map[x.argmax()], x.max()        

