"""
Module: sound

Module containing classes and functions for working with sound files,
specifically WAV files.

DO NOT MODIFY THIS FILE IN ANY WAY!!!!

Authors:
1) Sat Garcia @ USD
2) Dan Zingaro @ UToronto
"""

import math
import os
import sounddevice
import numpy
import scipy.io.wavfile
import matplotlib.pyplot as pp


"""
The Sample classes support the Sound class and allow manipulation of
individual sample values.
"""

class MonoSample():
    """
    A sample in a single-channeled Sound with a value.

    Properties:
        value (int): The sample's channel value.
    """

    def __init__(self, samp_array, i):
        """
        Create a MonoSample object based on a the sample data at a specific
        index in an array.
        """

        # negative indices are supported
        if -len(samp_array) <= i <= len(samp_array) - 1:
            self.samp_array = samp_array
            self.__index = i
        else:
            raise IndexError('Sample index out of bounds.')


    def __str__(self):
        """Return a string representation of this sample."""

        return "Sample at index " + str(self.__index) + " with channel value " \
            + str(self.value)

    @property
    def value(self):
        """(int) This sample's channel value."""

        return int(self.samp_array[self.__index])

    @value.setter
    def value(self, val):
        self.samp_array[self.__index] = int(val)

    def __eq__(self, other):
        return self.value == other.value


class StereoSample():
    """
    A sample in a two-channeled Sound with a left and a right value.

    Properties:
        left (int): The sample's left channel value.
        right (int): The sample's right channel value.
    """

    def __init__(self, all_samples, i):
        """
        Initialize a StereoSample object.

        Parameters:
            all_samples (numpy.ndarray): All the samples in the sound.
            i (int): Index where this sample is located.

        Raises:
            IndexError: If i isn't a valid index in all_samples
        """

        # negative indices are supported
        if -len(all_samples) <= i <= len(all_samples) - 1:
            self.__all_samples = all_samples
            self.__index = i
        else:
            raise IndexError('Sample index out of bounds.')


    def __str__(self):
        """Returns a string representation of this sample."""

        return "Sample at index " + str(self.__index) + " with a left channel value of " \
            + str(self.left) + " and a right value value of " + \
            str(self.right)


    @property
    def left(self):
        """(int) This sample's left channel value."""

        return int(self.__all_samples[self.__index, 0])

    @left.setter
    def left(self, new_left_val):
        if not isinstance(new_left_val, int):
            raise TypeError("Channel value must be an int")

        self.__all_samples[self.__index, 0] = new_left_val


    @property
    def right(self):
        """(int) This sample's right channel value."""

        return int(self.__all_samples[self.__index, 1])

    @right.setter
    def right(self, new_right_val):
        if not isinstance(new_right_val, int):
            raise TypeError("Channel value must be an int")

        self.__all_samples[self.__index, 1] = int(new_right_val)

    def __eq__(self, other):
        """
        Checks whether this sample and another are equal.
        Two samples are considered equal if their left and right channels have
        the same values.

        Parameters:
            other (SoundSample): Another sound sample to compare.

        Returns:
            equal (bool): Whether two samples are equal (True) or not (False)
        """

        return self.left == other.left \
                and self.right == other.right


class Sound():
    """
    A class representing audio. A sound object consists of a sequence of
    samples.

    Properties:
        sample_rate (int): The rate at which the sound was sampled, in samples
        per second.
    """

    def __init__(self, filename=None, samples=None):
        """
        Create a new Sound object.

        This new sound object is based either on a file (when filename is
        given) or an existing set of samples (when samples is given).
        If both filename and samples is given, the filename takes precedence
        and is used to create the new object.

        Parameters:
            filename (str, optional): The name of a file containing a wav encoded sound.
            samples ((int, numpy.ndarray), optional): Tuple containing sample rate and samples.

        Raises:
            RuntimeError: When neither filename or samples parameter is given.
        """

        self.__sample_encoding = numpy.dtype('int16')  # default encoding
        self.__set_filename(filename)

        if filename is not None:
            self.__sample_rate, sample_array = scipy.io.wavfile.read(filename)
            self.__samples = numpy.ndarray.copy(sample_array)

        elif samples is not None:
            self.__sample_rate, self.__samples = samples

        else:
            raise RuntimeError("No arguments were given to the Sound constructor.")

        if len(self.__samples.shape) == 1:
            self.__channels = 1
        else:
            self.__channels = self.__samples.shape[1]
        self.__sample_encoding = self.__samples.dtype


    def __eq__ (self, other):
        """
        Compares this Sound with another one.

        Two Sound objects are considered equal if they have the same number of
        channels and all of their samples match.

        Parameters:
            other (Sound): The sound to compare this one to.

        Returns:
            equal (bool): True if self and other are equal, false otherwise
        """
        if self.get_channels() == other.get_channels():
            return numpy.all(self.__samples == other.__samples)
        else:
            return False

    def __str__(self):
        """Return a string representation of this sound."""

        return "Sound with " + str(len(self)) + " samples."


    def __iter__(self):
        """Return an iterator to allow iterating through the samples in this
        sound."""

        if self.__channels == 1:
            for i in range(len(self)):
                yield MonoSample(self.__samples, i)

        elif self.__channels == 2:
            for i in range(len(self)):
                yield StereoSample(self.__samples, i)


    def __len__(self):
        """Return the number of samples in this sound."""

        return len(self.__samples)


    def __add__(self, second_sound):
        """
        Return a new Sound consisting of this Sound followed by another Sound.

        Parameters:
            second_sound (Sound): The sound object that will be the second part
            of the new sound.

        Returns:
            combined (Sound): A sound that begins with the samples in this sound
            and is followed by the samples in the other sound.
        """

        combined = self.copy()
        combined.append(second_sound)
        return combined


    def __mul__(self, num):
        """
        Return a new Sound that is this sound repeated multiple times.

        Parameters:
            num (int): The number of times to repeat this sound in the new sound.

        Returns:
            repeated (Sound): A sound that has the samples of this sound object
            repeated num times.
        """

        repeated = self.copy()
        for _ in range(int(num) - 1):
            repeated.append(self)
        return repeated


    def copy(self):
        """
        Create a copy of this Sound.

        This copy is "deep" in that modifying the samples in it will not affect
        this sound (and vice versa).

        Returns:
            new_copy (Sound): A deep copy of this sound.
        """

        return Sound(samples=(self.__sample_rate, self.__samples.copy()))


    def append_silence(self, num_samples):
        """
        Adds silence to the end of this sound.

        Parameters:
            num_samples (int): Number of (silent) samples added.

        Notes:
            Silence is represented by samples with 0 values for all the channels.
        """

        if self.__channels == 1:
            silence_array = numpy.zeros(num_samples, self.__sample_encoding)
        else:
            silence_array = numpy.zeros((num_samples, 2), self.__sample_encoding)

        self.append(Sound(samples=(self.__sample_rate, silence_array)))


    def append(self, snd):
        """
        Appends a Sound to the end of this one.

        Parameters:
            snd (Sound): The sound to append. It sound have the same number of
            channels as this sound (i.e. self).

        Raises:
            ValueError: When there is a mismatch in the number of channels in
            self and snd.
        """

        self.insert(snd, len(self))


    def insert(self, snd, i):
        """
        Inserts a sound into this one.

        Parameters:
            snd (Sound): The sound to insert. It sound have the same number of
            channels as this sound (i.e. self).
            i (int): The index in this sound where we will insert the other
            sound.

        Raises:
            ValueError: When there is a mismatch in the number of channels in
            self and snd.
        """

        if self.get_channels() != snd.get_channels():
            raise ValueError("Mismatch in number of channels.")
        else:
            first_chunk = self.__samples[:i]
            second_chunk = self.__samples[i:]
            new_samples = numpy.concatenate((first_chunk,
                                             snd.__samples,
                                             second_chunk))
            self.__samples = new_samples


    def crop(self, remove_before, remove_after):
        """
        Crops this sound.

        All samples before and after the specified indices are removed.

        Parameters:
            remove_before (int): Index before which all samples will be removed.
            May be negative.
            remove_after (int): Index after which all samples will be removed.
            May be negative.

        Raises:
            IndexError: If remove_before or remove_after are out of range.
        """

        if remove_before >= len(self) or remove_before < -len(self):
            raise IndexError("remove_before out of range:", remove_before)
        elif remove_after >= len(self) or remove_after < -len(self):
            raise IndexError("remove_after out of range:", remove_after)

        remove_before = remove_before % len(self)
        remove_after = remove_after % len(self)
        self.__samples = self.__samples[remove_before:remove_after + 1]


    def normalize(self):
        """
        Performs peak normalization on this sound.

        Notes:
            Peak normalization finds the maximum sample value and scales all
            samples so that this maximum sample value is now the maximum
            allowable sample value (e.g. 32767 for 16-bit samples).
        """

        maximum = self.__samples.max()
        minimum = self.__samples.min()
        factor = min(32767.0/maximum, 32767.0/abs(minimum))
        numpy.multiply(self.__samples, factor, out=self.__samples, casting='unsafe')


    def play(self, start_index=0, end_index=-1):
        """
        Plays part of the sound.

        Parameters:
            start_index (int, optional): The sample index where to start playing.
            end_index (int, optional): The sample index where to stop playing.

        Raises:
            IndexError: If start_index or end_index are out of range.
        """

        player = self.copy()
        player.crop(start_index, end_index)
        sounddevice.play(player.__samples, samplerate=self.__sample_rate)


    def stop(self):
        """Stop playing of this (and all other) sound."""
        sounddevice.stop()


    @property
    def sample_rate(self):
        """(int) The number of samples per second for this sound."""
        return self.__sample_rate


    def __getitem__(self, index):
        """
        Returns the sample at the specified index in this Sound.

        Parameters:
            index (int): The index of the desired sample. This may be negative.

        Raises:
            IndexError: When index is out of range.

        Returns:
            sample (MonoSample or StereoSample): The requested sample.
        """

        if index >= len(self) or index < -len(self):
            raise IndexError("index out of range:", index)

        if self.__channels == 1:
            return MonoSample(self.__samples, index)
        elif self.__channels == 2:
            return StereoSample(self.__samples, index)


    def get_max(self):
        """
        Return this sound's highest sample value.

        If this Sound is stereo return the absolute highest for both channels.
        """
        return self.__samples.max()


    def get_min(self):
        """
        Return this sound's lowest sample value.

        If this sound is stereo return the absolute lowest for both channels.
        """
        return self.__samples.min()


    def get_channels(self):
        """Return the number of channels in this sound."""
        return self.__channels


    def __set_filename(self, filename=None):
        """
        Associate a filename with this sound.

        If the filename is not given, then it is set to the empty string.

        Parameters:
            filename (str, optional): The name of the file, as a path. This
            should end with the extension ".wav" or ".WAV".

        Raises:
            ValueError: When the filename does not have a ".wav" or ".WAV"
            extension.
            OSError: When filename includes a path to a directory that doesn't
            currently exist.
        """

        if filename is not None:
            # First check that any path that might have been given is a valid
            # directory.
            head, tail = os.path.split(filename)
            if head != "" and not os.path.isdir(head):
                raise OSError(head, "does not exist.")

            # Next, check that we have a valid filename extension.
            file_extension = os.path.splitext(tail)[-1]
            if file_extension not in ['.wav', '.WAV']:
                raise ValueError("Filename must end in .wav or .WAV")

            self.__filename = filename
        else:
            self.__filename = ''



    def save_as(self, filename):
        """
        Save this sound to a specific file and set its filename.

        Parameters:
            filename (str): The name/path of the file. This should have either a
            '.wav' or '.WAV' extension.

        Raises:
            ValueError: When the filename does not have a ".wav" or ".WAV"
            extension.
            OSError: When filename includes a path to a directory that doesn't
            currently exist.
        """

        self.__set_filename(filename)
        scipy.io.wavfile.write(self.__filename, self.__sample_rate, self.__samples)


    def save(self):
        """
        Save this sound to a file, specifically to its set filename.

        Raises:
            ValueError: When no filename was set for this sound.
        """

        if self.__filename == "":
            raise ValueError("No filename set for this sound.")

        scipy.io.wavfile.write(self.__filename, self.__sample_rate, self.__samples)


    def display(self, figure_title=None):
        """
        Display the waveforms of the left and right channels of this sound.
        """
        time = numpy.linspace(0, len(self.__samples) / self.__sample_rate,
                              num=len(self.__samples))

        fig = pp.figure(figure_title)

        # FIXME: Don't assume Int32 values for samples or stereo sound
        pp.subplot(211, title="Left Channel", ylim=(-33000, 33000),
                   yticks=[-30000, -20000, -10000, 0, 10000, 20000, 30000])
        pp.plot(time, self.__samples[:, 0])

        pp.subplot(212, title="Right Channel", ylim=(-33000, 33000),
                   yticks=[-30000, -20000, -10000, 0, 10000, 20000, 30000])
        pp.plot(time, self.__samples[:, 1])

        pp.xlabel("Time (s)")

        pp.tight_layout()
        pp.show()


class Note(Sound):
    """
    A class that represents a musical note in the C scale.

    Notes are considered sounds: you can do anything with them that you can do
    with sounds, including combining them with other sounds.
    """

    # The frequency of notes of the C scale, in Hz
    frequencies = {'C' : 261.63,
                   'D' : 293.66,
                   'E' : 329.63,
                   'F' : 349.23,
                   'G' : 392.0,
                   'A' : 440.0,
                   'B' : 493.88}

    default_amp = 5000  # The default amplitude of a note.

    def __init__(self, note, note_length, octave=0):
        """
        Create a new note of a specific length and octave.

        Parameters:
            note (str): The name of the note: may be one of the following
            values: 'C', 'D', 'E', 'F', 'G', 'A', and 'B'
            note_length (int): The duration (in number of samples) of the note.
            octave (int, optional): The octave, relative to the 4th octave (e.g.
            1 will be the 5th octave, while -2 would be the 2nd octave).

        Raises:
            ValueError: When the note is not valid (e.g. "Q")

        Notes:
            Consecutive octaves of the same note (e.g. 'C') have frequencies
            that differ by a factor of 2. For example, the 4th octave of A
            is 440Hz while the 5th octave is 880Hz.
        """

        note = note.upper() # allow lower case by first changing them to upper

        if note not in self.frequencies:
            raise ValueError("Invalid note:", note)

        freq = int(self.frequencies[note] * (2.0 ** octave))
        samples = create_sine_wave(freq, self.default_amp, note_length)

        super().__init__(samples=(44100, samples))


"""
Helper Functions
"""

def create_sine_wave(frequency, amplitude, duration):
    """
    Creates an array with a sine wave of a specified frequency, amplitude,
    and duration.

    Parameters:
        frequency (float): The frequency of the sine wave.
        amplitude (int): The maximum amplitude of the sine wave.
        duration (int): The duration (in number of samples) of the sine wave.

    Returns:
        samples (numpy.array of numpy.int16): Array of samples with values
        modeling a sine wave of the given frequency and amplitude.
    """

    # Default frequency is in samples per second
    samples_per_second = 44100.0

    # Hz are periods per second
    seconds_per_period = 1.0 / frequency
    samples_per_period = samples_per_second * seconds_per_period

    samples = numpy.array([range(duration), range(duration)], numpy.float)
    samples = samples.transpose()

    # For each value in the array multiply it by 2*Pi, divide by the
    # samples per period, take the sin, and multiply the resulting
    # value by the amplitude.
    samples = numpy.sin((samples * 2.0 * math.pi) / samples_per_period) * amplitude
    envelope(samples, 2)

    # Convert the array back into one with the appropriate encoding
    samples = numpy.array(samples, numpy.dtype('int16'))
    return samples


def envelope(samples, channels):
    """
    Add an envelope to samples to prevent clicking.

    Parameters:
        samples (numpy.array): The samples to envelope.
        channels (int): The number of channels in each sample.
    """

    attack = 800
    if len(samples) < 3 * attack:
        attack = int(len(samples) * 0.05)

    line1 = numpy.linspace(0, 1, attack * channels)
    line2 = numpy.ones(len(samples) * channels - 2 * attack * channels)
    line3 = numpy.linspace(1, 0, attack * channels)
    enveloped = numpy.concatenate((line1, line2, line3))

    if channels == 2:
        enveloped.shape = (len(enveloped) // 2, 2)

    samples *= enveloped


"""
Global Sound Functions
"""

def load_sound(wav_filename):
    """
    Return a new Sound object from the audio data in the given file.

    The specified filename must be an uncompressed .wav file.
    """

    return Sound(filename=wav_filename)


def create_silent_sound(num_samples):
    """Return a silent Sound num_samples samples long."""

    if num_samples < 1:
        raise ValueError("Number of samples must be positive.")

    arr = [[0, 0] for i in range(num_samples)]
    npa = numpy.array(arr, dtype=numpy.dtype('int16'))

    return Sound(samples=(44100, npa))


def get_samples(snd):
    """Return a list of Samples in Sound snd."""

    return [samp for samp in snd]


def get_max_sample(snd):
    """Return Sound snd's highest sample value. If snd is stereo
    return the absolute highest for both channels."""

    return snd.get_max()


def get_min_sample(snd):
    """Return Sound snd's lowest sample value. If snd is stereo
    return the absolute lowest for both channels."""

    return snd.get_min()


def concatenate(snd1, snd2):
    """Return a new Sound object with Sound snd1 followed by Sound snd2."""

    return snd1 + snd2


def append_silence(snd, samp):
    """Append samp samples of silence onto Sound snd."""

    snd.append_silence(samp)


def append(snd1, snd2):
    """Append snd2 to snd1."""

    snd1.append(snd2)


def crop_sound(snd, first, last):
    """Crop snd Sound so that all Samples before int first and
    after int last are removed. Cannot crop to a single sample.
    Negative indices are supported."""

    snd.crop(first, last)


def insert(snd1, snd2, i):
    """Insert Sound snd2 in Sound snd1 at index i."""

    snd1.insert(snd2, i)


def play(snd):
    """Play Sound snd from beginning to end."""

    snd.play()


def play_in_range(snd, first, last):
    """Play Sound snd from index first to last."""

    snd.play(first, last)


def save_as(snd, filename):
    """Save sound snd to filename."""

    snd.save_as(filename)


def stop():
    """Stop playing Sound snd."""

    sounddevice.stop()


def wait_until_played():
    """Waits until all sounds are done playing."""

    sounddevice.wait()


"""
Global Sample Functions
"""

def copy(obj):
    """Return a deep copy of sound obj."""

    return obj.copy()

