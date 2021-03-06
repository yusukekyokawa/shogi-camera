import os
import click
import shogicam
import shogicam.util
import shogicam.data
import shogicam.learn
import shogicam.preprocess
import shogicam.predict

@click.group(help='Shogi Camera')
def main():
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    pass

@main.command(help='Predict shogi board contents')
@click.argument('img_path', type=click.Path(exists=True))
@click.option('--model-path', '-m', default='models/blue3.h5')
def predict(img_path, model_path):
    raw_img = shogicam.util.load_img(img_path)
    corners, score = shogicam.preprocess.detect_corners(raw_img)
    board = shogicam.preprocess.trim_board(raw_img, corners)
    print("corner detection score: %f" % score)

    result = shogicam.predict.predict_board(board, model_path)
    for row in result.reshape((9, 9)):
        row_labels = [shogicam.util.label_name(c) for c in row]
        print(' '.join(row_labels))

@main.command(help='Fit model')
@click.option('--data-dir', '-d', type=click.Path(exists=True), default='data')
@click.option('--outmodel-path', '-o', type=click.Path(), default='models/blue3.h5')
@click.option('--model', '-m', default='blue3')
def learn(data_dir, outmodel_path, model):
    model = shogicam.learn.learn_model(model, data_dir, verbose=True)
    shogicam.learn.save_model(model, outmodel_path)

@main.command(help='Eval model')
@click.argument('model_path', type=click.Path(exists=True))
@click.option('--sente', '-s', is_flag=True)
@click.option('--data-dir', '-d', type=click.Path(exists=True), default='data/board')
def eval_model(model_path, sente, data_dir):
    x, y = shogicam.data.load_validation_cells(data_dir, sente, True)
    shogicam.predict.eval_model(model_path, x, y)
    print()
    data = shogicam.data.load_validation_board_data(data_dir, sente, True)
    for (i, (x, y)) in enumerate(data):
        print("board {}".format(i + 1))
        shogicam.predict.eval_model(model_path, x, y)

@main.group(help='Generate train data')
def gen_traindata():
    pass

@gen_traindata.command(help='Generate koma train data')
@click.option('--img-dir', '-i', type=click.Path(exists=True), default='images/koma')
@click.option('--outdata-dir', '-o', type=click.Path(exists=True), default='data/koma')
def koma(img_dir, outdata_dir):
    result = shogicam.data.gen_koma_traindata(img_dir, outdata_dir)
    print(result)

@gen_traindata.command(help='Generate empty cell train data')
@click.option('--img-dir', '-i', type=click.Path(exists=True), default='images/empty_cell')
@click.option('--outdata-path', '-o', type=click.Path(), default='data/empty_cell.npz')
def empty_cell(img_dir, outdata_path):
    result = shogicam.data.gen_empty_cell_traindata(img_dir, outdata_path)
    print(result)

@gen_traindata.command(help='Generate etl8 data')
@click.option('--etl8-dir', '-i', type=click.Path(exists=True), default='ETL8G')
@click.option('--outdata-path', '-o', type=click.Path(), default='data/etl8.npz')
def etl8(etl8_dir, outdata_path):
    shogicam.data.gen_etl8(etl8_dir, outdata_path)
    print('finished')

@gen_traindata.command(help='Generate validation board data')
@click.option('--img-dir', '-i', type=click.Path(exists=True), default='images/board')
@click.option('--outdata-path', '-o', type=click.Path(), default='data/board/cells.npy')
def validation_board(img_dir, outdata_path):
    shogicam.data.gen_validation_board(img_dir, outdata_path)
    print('finished')

if __name__ == '__main__':
    main()
