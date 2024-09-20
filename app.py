from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# língua portuguesa
frequencia_portugues = [0.1463, 0.0104, 0.0388, 0.0499, 0.1257, 0.0102, 0.0130,
                          0.0078, 0.0618, 0.0039, 0.0001, 0.0278, 0.0474, 0.0505,
                          0.1073, 0.0252, 0.0120, 0.0653, 0.0781, 0.0434, 0.0463,
                          0.0167, 0.0001, 0.0021, 0.0001, 0.0047]

# língua inglesa
frequencia_ingles = [0.08167, 0.01492, 0.02782, 0.04253, 0.12702, 0.02228, 0.02015,
					  0.06094, 0.06966, 0.00153, 0.00772, 0.04025, 0.02406, 0.06749,
					  0.07507, 0.01929, 0.00095, 0.05987, 0.06327, 0.09056, 0.02758,
					  0.00978, 0.02360, 0.00150, 0.01974, 0.00074]

TAMANHO_MAX_CHAVE = 20

alfabeto = 'abcdefghijklmnopqrstuvwxyz'

# índice de coincidência
def indiceCoincidencia(cifrado):
    N = float(len(cifrado))
    somaFreq = 0.0
    for letra in alfabeto:
        somaFreq += cifrado.count(letra) * (cifrado.count(letra) - 1)
    indice = somaFreq / (N * (N - 1))
    return indice

# tamanho da chave (maior média de IC)
def tamanhoChave(cifrado):
    tabelaIndice = []
    for keyLength in range(TAMANHO_MAX_CHAVE):
        somaIndiceCoincidencia = 0.0
        mediaICLength = 0.0
        for i in range(keyLength):
            sequencia = ""
            for j in range(0, len(cifrado[i:]), keyLength):
                sequencia += cifrado[i + j]
            somaIndiceCoincidencia += indiceCoincidencia(sequencia)
        if keyLength != 0:
            mediaICLength = somaIndiceCoincidencia / keyLength
        tabelaIndice.append(mediaICLength)

    # (comprimento de chave mais provável)
    melhorChave = tabelaIndice.index(sorted(tabelaIndice, reverse=True)[0])
    melhorChave2 = tabelaIndice.index(sorted(tabelaIndice, reverse=True)[1])

    if melhorChave % melhorChave2 == 0:
        return melhorChave2
    else:
        return melhorChave

def frequenciaPortugues(sequencia):
    listaDeslocamentos = [0] * 26

    for i in range(26):

        deslocamentoAtual = 0.0

        sequenciaDeslocada = [chr(((ord(sequencia[j]) - 97 - i) % 26) + 97) for j in range(len(sequencia))]
        v = [0] * 26
        for l in sequenciaDeslocada:
            v[ord(l) - ord('a')] += 1
        for j in range(26):
            v[j] *= (1.0 / float(len(sequencia)))

        # compara com as frequências em português
        for j in range(26):
            deslocamentoAtual += ((v[j] - float(frequencia_portugues[j])) ** 2) / float(frequencia_portugues[j])

        listaDeslocamentos[i] = deslocamentoAtual

    letraDeslocamento = listaDeslocamentos.index(min(listaDeslocamentos))
    return chr(letraDeslocamento + 97)

def frequenciaIngles(sequencia):
    listaDeslocamentos = [0] * 26

    for i in range(26):
        deslocamentoAtual = 0.0
        sequenciaDeslocada = [chr(((ord(sequencia[j]) - 97 - i) % 26) + 97) for j in range(len(sequencia))]
        v = [0] * 26
        for l in sequenciaDeslocada:
            v[ord(l) - ord('a')] += 1
        for j in range(26):
            v[j] *= (1.0 / float(len(sequencia)))

        for j in range(26):
            deslocamentoAtual += ((v[j] - float(frequencia_ingles[j])) ** 2) / float(frequencia_ingles[j])

        listaDeslocamentos[i] = deslocamentoAtual
    letraDeslocamento = listaDeslocamentos.index(min(listaDeslocamentos))
    return chr(letraDeslocamento + 97)

def chavePortugues(cifrado, key_length):
    key = ''

    for i in range(key_length):
        sequencia = ""
        for j in range(0, len(cifrado[i:]), key_length):
            sequencia += cifrado[i + j]
        key += frequenciaPortugues(sequencia)

    return key

def chaveIngles(cifrado, key_length):
    key = ''
    for i in range(key_length):
        sequencia = ""
        for j in range(0, len(cifrado[i:]), key_length):
            sequencia += cifrado[i + j]
        key += frequenciaIngles(sequencia)

    return key

def decifrar(cifrado, key):
    cipher_ascii = [ord(letra) for letra in cifrado]
    key_ascii = [ord(letra) for letra in key]
    plain_ascii = []
    for i in range(len(cipher_ascii)):
        plain_ascii.append(((cipher_ascii[i] - key_ascii[i % len(key)]) % 26) + 97)

    plaintext = ''.join(chr(i) for i in plain_ascii)
    return plaintext

@app.route('/')
def serve_index():
    return send_from_directory('', 'index.html')

@app.route('/decifrar', methods=['POST'])
def decifrar_route():
    data = request.json
    cifrado = data['cifrado']

    cifrado = ''.join(x.lower() for x in cifrado if x.isalpha())    

    key_length = tamanhoChave(cifrado)
    keyPortugues = chavePortugues(cifrado, key_length)
    keyIngles = chaveIngles(cifrado, key_length)
    plaintextPortugues = decifrar(cifrado, keyPortugues)
    plaintextIngles = decifrar(cifrado, keyIngles)

    return jsonify({
        'keyPortugues': keyPortugues,
        'plaintextPortugues': plaintextPortugues,
        'keyIngles': keyIngles,
        'plaintextIngles': plaintextIngles
    })

if __name__ == '__main__':
    app.run(debug=True)