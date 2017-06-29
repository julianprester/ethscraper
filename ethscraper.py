import requests
import pandas as pd
import numpy as np

output_dir = './data/'
base_url ='http://api.etherscan.io/api?module=account&action=txlist&address={}&startblock=0&endblock=99999999&sort=asc'
address = '0x687aeda127fd2bd4f374c73e3724bf9b7c7a6b9c'

def get_transactions(addr):
    """Make an Etherscan API request convert the resulting JSON response to a Pandas dataframe

    Parameters
    ----------
    addr : string
        The ETH address which transactions are to be analyzed

    Returns
    -------
    df : Pandas dataframe
        The Etherscan API response as a Pandas dataframe
    """
    r = requests.get(base_url.format(addr))
    return pd.DataFrame(r.json()['result'])

def preprocess(df):
    """Preprocess the transaction data before saving to csv files

    Parameters
    ----------
    df : Pandas dataframe
        The Etherscan API response as a Pandas dataframe

    Returns
    -------
    df : Pandas dataframe
        The preprocessed Pandas dataframe
    """
    df.drop(df.columns[[0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 15]], axis=1, inplace=True)

    df['value'] = df['value'].astype(float)
    df['value'] = df['value'] / 1000000000000000000
    df = df.loc[np.abs(df['value'] - df['value'].mean()) <= (3 * df['value'].std()), :]

    df['timeStamp'] = df['timeStamp'].astype(int)
    df['timeStamp'] = pd.to_datetime(df['timeStamp'], unit='s')
    df['timeStamp'] = df['timeStamp'].apply(lambda x: x.date())
    df.columns = ['from', 'date', 'to', 'value']
    df = df[['date', 'from', 'to', 'value']]
    return df

def build_incoming_data(df):
    """Build the dataframe for the incoming transactions plot

    Parameters
    ----------
    df : Pandas dataframe
        The preprocessed Pandas dataframe
    """
    df = df[df['to'] == address].loc[:, ['date', 'value']]
    df = df.groupby('date', as_index=False).sum()
    df = df.set_index('date', drop=True)
    idx = pd.date_range(df.index.min(), df.index.max())
    df = df.reindex(idx, fill_value=0)
    df['cumulative'] = df.value.cumsum()
    df.to_csv(output_dir + 'incoming.csv', index=True, index_label='date')

def build_outgoing_data(df):
    """Build the dataframe for the outgoing transactions plot

    Parameters
    ----------
    df : Pandas dataframe
        The preprocessed Pandas dataframe
    """
    df = df[df['from'] == address].loc[:, ['date', 'value']]
    df = df.groupby('date').sum()
    idx = pd.date_range(df.index.min(), df.index.max())
    df = df.reindex(idx, fill_value=0)
    df['cumulative'] = df.value.cumsum()
    df.to_csv(output_dir + 'outgoing.csv', index=True, index_label='date')

def build_address_data(df):
    """Build the dataframe for the unique addresses plot

    Parameters
    ----------
    df : Pandas dataframe
        The preprocessed Pandas dataframe
    """
    df = df[df['to'] == address].loc[:, ['date', 'from']]
    df = df.groupby('from', as_index=False).min()
    df = df.groupby('date').count()
    df.columns = ['value']
    idx = pd.date_range(df.index.min(), df.index.max())
    df = df.reindex(idx, fill_value=0)
    df['cumulative'] = df.value.cumsum()
    df.to_csv(output_dir + 'address.csv', index=True, index_label='date')

def main():
    df = get_transactions(address)
    df = preprocess(df)
    build_incoming_data(df)
    build_outgoing_data(df)
    build_address_data(df)

if __name__ == '__main__':
    main()
