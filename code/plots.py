#!/usr/bin/env python3
import matplotlib.pyplot as plt

import matplotlib
import numpy as np

import tensorflow_probability as tfp

from util import substitute
from model_wrapper import ModelWrapper, ModelMockup

tfpl = tfp.layers
tfd = tfp.distributions

COLUMN_WIDTH = 252.0  # pt
INCHES_PER_PT = 1.0 / 72.27
GOLDEN_MEAN = (np.sqrt(5) - 1.0) / 2.0


def plot_comparison_disentanglement(imgs: list, models: list, model_names: list, feature_dict: dict, min_z=-6,
                                    max_z=6, num_steps=6, range_dict=None, substitution_dict=None):
    if substitution_dict is None:
        substitution_dict = {}
    if range_dict is None:
        range_dict = {}
    fig_width = COLUMN_WIDTH * 2 * INCHES_PER_PT
    fig_height = fig_width * GOLDEN_MEAN
    fig_size = [fig_width, fig_height]

    matplotlib.use("pgf")
    matplotlib.rcParams.update({
        "pgf.texsystem": "pdflatex",
        'font.family': 'serif',
        'text.usetex': True,
        'pgf.rcfonts': False,
        'figure.figsize': fig_size
    })

    fig, axs = plt.subplots(len(feature_dict), len(models), sharex='all', sharey='all', figsize=fig_size)

    for i, feature_name in enumerate(feature_dict.keys()):
        for j, (model, model_name) in enumerate(zip(models, model_names)):
            min_z_temp, max_z_temp = range_dict[model_name] if model_name in range_dict else (min_z, max_z)

            plot_image_matrix(imgs, model, feature_dict[feature_name][j], axs[i, j], min_z=min_z_temp,
                              max_z=max_z_temp, num_steps=num_steps)

    for ax, col in zip(axs[-1, :], model_names):
        min_z_temp, max_z_temp = range_dict[col] if col in range_dict else (min_z, max_z)
        if col in substitution_dict:
            col = substitute(col, substitution_dict)
        ax.set_xlabel(f'{col} ({min_z_temp},{max_z_temp})')

    for ax, row in zip(axs[:, 0], feature_dict.keys()):
        ax.set_ylabel(row)

    plt.tight_layout()
    plt.subplots_adjust(wspace=0.1, hspace=0.1)
    return fig, axs


def plot_image_matrix(imgs, model, feature_dimension, ax, min_z=-5, max_z=5, num_steps=6):
    img_width, img_height, channels = imgs[0].shape
    canvas = np.zeros((len(imgs) * img_height, num_steps * img_width, channels))
    steps = np.linspace(min_z, max_z, num_steps)
    for j, img in enumerate(imgs):
        z = np.array(model.get_latent(img))
        for i, step in enumerate(steps):
            z[feature_dimension] = step
            reconstruction = model.get_reconstruction(z)
            canvas[j * img_width: (j + 1) * img_width, i * img_height: (i + 1) * img_height] = reconstruction

    ax.imshow(canvas)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.tick_params(axis='both', which='both', length=0)


def plot_comparison_generative(models: list, model_names: list, size=(5, 5),
                               substitution_dict=None):
    if substitution_dict is None:
        substitution_dict = {}
    fig_width = COLUMN_WIDTH * INCHES_PER_PT
    fig_height = fig_width * GOLDEN_MEAN
    fig_size = [fig_width, fig_height]

    matplotlib.use("pgf")
    matplotlib.rcParams.update({
        "pgf.texsystem": "pdflatex",
        'font.family': 'serif',
        'text.usetex': True,
        'pgf.rcfonts': False,
        'figure.figsize': fig_size
    })

    fig, axs = plt.subplots(1, len(models), figsize=fig_size)

    for model, ax in zip(models, axs):
        plot_generative_matrix(model, ax, size)

    for ax, col in zip(axs, model_names):
        if col in substitution_dict:
            col = substitute(col, substitution_dict)
        ax.set_xlabel(col)

    plt.tight_layout()
    plt.subplots_adjust(wspace=0.1, hspace=0.1)
    return fig, axs


def plot_generative_matrix(model, ax, size=(5, 5)):
    cols, rows = size
    img_width, img_height, channels = model.output_shape
    canvas = np.zeros((cols * img_width, rows * img_height, channels))

    for j in range(cols):
        for i in range(rows):
            img = model.sample()
            canvas[j * img_width: (j + 1) * img_width, i * img_height: (i + 1) * img_height] = img

    ax.imshow(canvas)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.tick_params(axis='both', which='both', length=0)


def plot_model_exploration(model: ModelWrapper, img: np.array, min_z: float = -6, max_z: float = 6,
                           num_steps: int = 10):
    img_height, img_width, channels = model.output_shape
    steps = np.linspace(-15, 15, num_steps)
    canvas = np.zeros((model.latent_dim * img_height, num_steps * img_width, channels))
    fig, ax = plt.subplots()
    z = model.get_latent(img)

    for j in range(model.latent_dim):
        z_temp = np.copy(z)

        for i, step in enumerate(steps):
            z_temp[j] = step
            reconstruction = model.get_reconstruction(z_temp)
            canvas[j * img_width : (j + 1) * img_width, i * img_height : (i + 1) * img_height] = reconstruction

    ax.imshow(canvas)
    start_range_y = img_height // 2
    end_range_y = model.latent_dim * img_height + start_range_y
    pixel_range_y = np.arange(start_range_y, end_range_y, img_height)
    ax.set_yticks(pixel_range_y)
    ax.set_yticklabels(list(range(model.latent_dim)), fontsize=8)
    ax.set_xticks([])
    ax.set_xticklabels([])

    return fig, ax


def plot_comparison_reconstruction(imgs: list, models: list, model_names: list, substitution_dict=None):
    if substitution_dict is None:
        substitution_dict = {}

    fig_width = COLUMN_WIDTH * INCHES_PER_PT
    fig_height = fig_width * GOLDEN_MEAN
    fig_size = [fig_width, fig_height]

    matplotlib.use("pgf")
    matplotlib.rcParams.update({
        "pgf.texsystem": "pdflatex",
        'font.family': 'serif',
        'text.usetex': True,
        'pgf.rcfonts': False,
        'figure.figsize': fig_size
    })

    fig, axs = plt.subplots(1, len(models) + 1, figsize=fig_size)

    for model, ax in zip([ModelMockup(imgs[0], 1)] + models, axs):
        plot_reconstruction_matrix(imgs, model, ax)

    axs[0].set_xlabel('Original')

    for ax, col in zip(axs[1:], model_names):
        if col in substitution_dict:
            col = substitute(col, substitution_dict)
        ax.set_xlabel(col)

    plt.tight_layout()
    plt.subplots_adjust(wspace=0.1, hspace=0.1)
    return fig, axs


def plot_reconstruction_matrix(imgs: list, model, ax):
    img_width, img_height, channels = model.output_shape
    canvas = np.zeros((img_height * len(imgs), img_width, channels))
    for j, img in enumerate(imgs):
        reconstruction = model.get_reconstruction(model.get_latent(img))
        canvas[j * img_height: (j + 1) * img_height, :] = reconstruction

    ax.imshow(canvas)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.tick_params(axis='both', which='both', length=0)
